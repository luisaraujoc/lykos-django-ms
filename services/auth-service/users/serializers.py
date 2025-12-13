from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Usuario, Pessoa, Endereco

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'nome_usuario', 'email', 'tipo', 'status', 'data_criacao']

class PessoaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pessoa
        fields = '__all__'

class EnderecoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Endereco
        fields = '__all__'

class RegisterSerializer(serializers.ModelSerializer):
    pessoa = PessoaSerializer()
    enderecos = EnderecoSerializer(many=True, required=False)

    class Meta:
        model = Usuario
        fields = ['nome_usuario', 'email', 'senha_hash', 'tipo', 'pessoa', 'enderecos']

    def create(self, validated_data):
        pessoa_data = validated_data.pop('pessoa')
        enderecos_data = validated_data.pop('enderecos', [])
        user = Usuario.objects.create_user(**validated_data)
        Pessoa.objects.create(usuario=user, **pessoa_data)
        for endereco in enderecos_data:
            Endereco.objects.create(usuario=user, **endereco)
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user_id'] = self.user.id
        data['tipo'] = self.user.tipo
        data['email'] = self.user.email
        return data