import json
from rest_framework import serializers
from django.db import transaction
from .models import (
    Freelancer,
    Formacao,
    Habilidade,
    Idioma,
    FreelancerIdioma,
    PortfolioProject,
    PortfolioItem
)
from shared.enums import NivelIdioma


# === Serializers Auxiliares (Leitura) ===

class IdiomaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Idioma
        fields = ['id', 'nome', 'iso_codigo']


class HabilidadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habilidade
        fields = ['id', 'nome']


class FormacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Formacao
        fields = ['id', 'titulo', 'instituicao', 'ano_conclusao']


# === Serializer Principal (Escrita) ===

class TornarSeFreelancerSerializer(serializers.ModelSerializer):
    # Mapeamento dos campos do frontend para o model
    nome = serializers.CharField(source='nome_exibicao')
    descricao = serializers.CharField(source='bio')
    fotoPerfil = serializers.ImageField(source='foto_perfil')

    # Campos que recebem dados brutos (Strings ou Listas) do FormData
    skills = serializers.ListField(child=serializers.CharField(), write_only=True)
    idiomas = serializers.JSONField(write_only=True)
    formacoes = serializers.JSONField(write_only=True)

    class Meta:
        model = Freelancer
        fields = ['nome', 'descricao', 'fotoPerfil', 'skills', 'idiomas', 'formacoes']

    def to_internal_value(self, data):
        """
        Converte QueryDict (Multipart) para Dict Python puro para manipulação segura de JSON.
        """
        # 1. Converte para dicionário Python padrão
        # Se for um QueryDict (envio de arquivo), usamos .lists() para preservar listas (como skills)
        if hasattr(data, 'lists'):
            mutable_data = {}
            for key, value in data.lists():
                # 'skills' é uma lista de strings, mantemos a lista inteira
                if key == 'skills':
                    mutable_data[key] = value
                # Para outros campos (inclusive arquivos), pegamos apenas o primeiro item
                # (comportamento padrão de formulários multipart)
                elif len(value) > 0:
                    mutable_data[key] = value[0]
        else:
            # Fallback se vier como JSON puro (testes unitários, etc)
            mutable_data = data.copy()

        # 2. Parse manual das strings JSON para Objetos Python
        for field_name in ['idiomas', 'formacoes']:
            if field_name in mutable_data:
                value = mutable_data[field_name]
                if isinstance(value, str):
                    try:
                        # Converte string '[{...}]' para lista python [{...}]
                        mutable_data[field_name] = json.loads(value)
                    except (ValueError, TypeError):
                        # Se o JSON for inválido, passamos em branco ou deixamos o DRF validar
                        # Aqui escolhemos passar o valor original para o DRF retornar o erro padrão se falhar
                        pass

        return super().to_internal_value(mutable_data)

    def create(self, validated_data):
        # O ID do usuário vem do Token (injetado pela StatelessAuth no request)
        user_id = self.context['request'].user.id

        # Remove os campos "extras" para não dar erro no create do Model principal
        skills_names = validated_data.pop('skills', [])
        idiomas_data = validated_data.pop('idiomas', [])
        formacoes_data = validated_data.pop('formacoes', [])

        with transaction.atomic():
            # 1. Cria ou Atualiza o Freelancer
            freelancer, created = Freelancer.objects.update_or_create(
                id=user_id,
                defaults={
                    'nome_exibicao': validated_data.get('nome_exibicao'),
                    'bio': validated_data.get('bio'),
                    'foto_perfil': validated_data.get('foto_perfil')
                }
            )

            # 2. Habilidades (Many-to-Many)
            if skills_names:
                freelancer.habilidades.clear()
                for name in skills_names:
                    # Capitalize para padronizar (Python vs python)
                    skill_obj, _ = Habilidade.objects.get_or_create(nome=name.capitalize())
                    freelancer.habilidades.add(skill_obj)

            # 3. Idiomas (Tabela Intermediária com Nível)
            if idiomas_data:
                FreelancerIdioma.objects.filter(freelancer=freelancer).delete()
                for item in idiomas_data:
                    nome_idioma = item.get('nome')
                    nivel = item.get('nivel', 'BASICO')  # Valor padrão se não vier

                    if nome_idioma:
                        # Tenta encontrar ou cria o idioma base
                        idioma_obj, _ = Idioma.objects.get_or_create(
                            nome__iexact=nome_idioma,
                            defaults={
                                'nome': nome_idioma,
                                'iso_codigo': nome_idioma[:2].upper()
                            }
                        )
                        # Cria a relação com nível
                        FreelancerIdioma.objects.create(
                            freelancer=freelancer,
                            idioma=idioma_obj,
                            nivel=nivel
                        )

            # 4. Formações (One-to-Many)
            if formacoes_data:
                freelancer.formacoes.all().delete()
                for form in formacoes_data:
                    Formacao.objects.create(
                        freelancer=freelancer,
                        titulo=form.get('titulo'),
                        instituicao=form.get('instituicao'),
                        ano_conclusao=form.get('ano')
                    )

        return freelancer


# === Outros Serializers ===

class FreelancerSerializer(serializers.ModelSerializer):
    skills = serializers.StringRelatedField(many=True, source='habilidades')
    formacoes = FormacaoSerializer(many=True)

    class Meta:
        model = Freelancer
        fields = '__all__'


class PortfolioItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioItem
        fields = '__all__'