import json
from rest_framework import serializers
from django.db import transaction
from .models import Freelancer, Formacao, Habilidade, Idioma, FreelancerIdioma
from shared.enums import NivelIdioma


class FormacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Formacao
        fields = ['titulo', 'instituicao', 'ano_conclusao']


class TornarSeFreelancerSerializer(serializers.ModelSerializer):
    # Campos recebidos do Front
    nome = serializers.CharField(source='nome_exibicao')
    descricao = serializers.CharField(source='bio')
    fotoPerfil = serializers.ImageField(source='foto_perfil', required=True)

    # Listas de Strings (como vem do Vue)
    skills = serializers.ListField(child=serializers.CharField(), write_only=True)
    idiomas = serializers.ListField(child=serializers.CharField(), write_only=True)

    # Formação (Front manda um objeto único, mas backend suporta lista. Adaptamos aqui.)
    # Se o front mandar JSON string dentro do multipart, precisaremos de um parser customizado,
    # mas vamos assumir que o DRF lida com nested fields se configurado corretamente no front.
    # Para simplificar e garantir funcionamento com Multipart, vamos receber como JSON string se necessário,
    # ou campos individuais se for só uma formação.
    # Dado o código Vue: `form.formacao` é um objeto.
    formacao = serializers.JSONField(write_only=True, required=True)

    class Meta:
        model = Freelancer
        fields = ['nome', 'descricao', 'fotoPerfil', 'skills', 'idiomas', 'formacao']

    def create(self, validated_data):
        # 1. Extrair dados das relações
        skills_names = validated_data.pop('skills', [])
        idiomas_names = validated_data.pop('idiomas', [])
        formacao_data = validated_data.pop('formacao', {})

        # O ID do freelancer é o ID do usuário logado (passado via save(id=user_id))
        user_id = self.context['request'].user.id

        with transaction.atomic():
            # 2. Criar ou Atualizar o Freelancer
            freelancer, created = Freelancer.objects.update_or_create(
                id=user_id,
                defaults={
                    'nome_exibicao': validated_data.get('nome_exibicao'),
                    'bio': validated_data.get('bio'),
                    'foto_perfil': validated_data.get('foto_perfil')
                }
            )

            # 3. Salvar Habilidades (Busca na lista do Fiverr ou Cria nova)
            if skills_names:
                freelancer.habilidades.clear()  # Limpa anteriores se for edição
                for name in skills_names:
                    # get_or_create permite que o usuário adicione skills novas não listadas
                    skill_obj, _ = Habilidade.objects.get_or_create(nome=name)
                    freelancer.habilidades.add(skill_obj)

            # 4. Salvar Idiomas
            # Aqui assumimos que o idioma JÁ EXISTE no seed (pela validação do front).
            # Se não existir, ignoramos ou criamos. Vamos buscar pelo nome.
            if idiomas_names:
                FreelancerIdioma.objects.filter(freelancer=freelancer).delete()
                for idioma_nome in idiomas_names:
                    try:
                        idioma_obj = Idioma.objects.get(nome__iexact=idioma_nome)
                        # Como o front não manda nível, definimos um padrão ou criamos lógica futura
                        # Por enquanto, salvamos como "Nativo" ou "Fluente" padrão
                        FreelancerIdioma.objects.create(
                            freelancer=freelancer,
                            idioma=idioma_obj,
                            nivel=NivelIdioma.FLUENTE  # Default provisório
                        )
                    except Idioma.DoesNotExist:
                        pass  # Ignora idioma não reconhecido no banco

            # 5. Salvar Formação
            # O front manda um objeto simples: {titulo, instituicao, ano}
            if formacao_data:
                freelancer.formacoes.all().delete()  # Substitui as anteriores
                Formacao.objects.create(
                    freelancer=freelancer,
                    titulo=formacao_data.get('titulo'),
                    instituicao=formacao_data.get('instituicao'),
                    ano_conclusao=formacao_data.get('ano')
                )

        return freelancer