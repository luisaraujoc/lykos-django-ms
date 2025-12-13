# users/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from allauth.socialaccount.models import SocialAccount
from .models import Usuario, Pessoa

@receiver(post_save, sender=SocialAccount)
def create_pessoa_from_google(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        extra_data = instance.extra_data

        # Pega nome do Google
        nome_completo = extra_data.get('name', '').strip()
        if not nome_completo and '@' in user.email:
            nome_completo = user.email.split('@')[0].title()

        Pessoa.objects.get_or_create(
            usuario=user,
            defaults={
                'nome_completo': nome_completo,
                'cpf': '',
                'data_nascimento': None,
                'telefone': ''
            }
        )