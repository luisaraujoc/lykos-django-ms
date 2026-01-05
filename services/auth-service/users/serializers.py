from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from shared.utils import validate_cpf
from .models import Usuario, Pessoa, Endereco


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'nome_usuario', 'email', 'tipo', 'status', 'data_criacao']


class PessoaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pessoa
        fields = ['nome_completo', 'cpf', 'data_nascimento', 'telefone']

    def validate_cpf(self, value):
        # Remove caracteres não numéricos para salvar limpo ou validar
        clean_cpf = ''.join(filter(str.isdigit, value))

        try:
            # Usa sua função do shared/utils.py
            validate_cpf(clean_cpf)
        except DjangoValidationError as e:
            # Converte erro do Django para erro do DRF (aparece bonito no JSON)
            raise serializers.ValidationError(str(e.message))

        return clean_cpf


class EnderecoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Endereco
        fields = ['tipo', 'logradouro', 'numero', 'complemento', 'cep', 'cidade', 'estado']


class RegisterSerializer(serializers.ModelSerializer):
    pessoa = PessoaSerializer()
    enderecos = EnderecoSerializer(many=True, required=False)
    senha2 = serializers.CharField(write_only=True, required=True, label="Confirmar Senha")

    class Meta:
        model = Usuario
        fields = ['nome_usuario', 'email', 'senha_hash', 'senha2', 'tipo', 'pessoa', 'enderecos']
        extra_kwargs = {'senha_hash': {'write_only': True, 'label': 'Senha'}}

    def validate(self, data):
        if data.get('senha_hash') != data.get('senha2'):
            raise serializers.ValidationError({"senha2": "As senhas não conferem."})
        return data

    def create(self, validated_data):
        pessoa_data = validated_data.pop('pessoa')
        enderecos_data = validated_data.pop('enderecos', [])
        validated_data.pop('senha2')
        senha = validated_data.pop('senha_hash')

        # Atomicidade: Garante que tudo é criado ou nada é criado
        with transaction.atomic():
            # Cria o usuário usando o helper que faz o hash da senha
            user = Usuario.objects.create_user(senha=senha, **validated_data)

            # Cria a Pessoa vinculada
            Pessoa.objects.create(usuario=user, **pessoa_data)

            # Cria os Endereços vinculados
            for endereco in enderecos_data:
                Endereco.objects.create(usuario=user, **endereco)

        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Adiciona dados ao Payload do JWT (Decodificável pelo Traefik e Front)
        token['name'] = user.nome_usuario
        token['email'] = user.email
        token['tipo'] = user.tipo
        token['user_id'] = user.id  # Crucial para o X-User-Id

        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Retorna dados básicos no corpo da resposta do login também
        data['user'] = {
            'id': self.user.id,
            'email': self.user.email,
            'nome_usuario': self.user.nome_usuario,
            'tipo': self.user.tipo
        }
        return data