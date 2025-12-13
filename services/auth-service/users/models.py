from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from shared.enums import TipoUsuario, StatusConta, TipoEndereco  # Do shared/


class UserManager(BaseUserManager):
    def create_user(self, email, nome_usuario, senha=None, **extra_fields):
        if not email:
            raise ValueError("Email obrigatório")
        email = self.normalize_email(email)
        user = self.model(email=email, nome_usuario=nome_usuario, **extra_fields)
        user.set_password(senha)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nome_usuario, senha=None, **extra_fields):
        extra_fields.setdefault("tipo", TipoUsuario.ADMIN)
        extra_fields.setdefault("status", StatusConta.ATIVO)
        return self.create_user(email, nome_usuario, senha, **extra_fields)


class Usuario(AbstractBaseUser):
    id = models.BigAutoField(primary_key=True)
    nome_usuario = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    senha_hash = models.CharField(max_length=255)  # Não use, set_password faz hash
    tipo = models.CharField(
        max_length=20, choices=TipoUsuario.choices, default=TipoUsuario.CLIENTE
    )
    status = models.CharField(
        max_length=20, choices=StatusConta.choices, default=StatusConta.ATIVO
    )
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    is_social = models.BooleanField(default=False)  # saber se veio do Google
    avatar_url = models.URLField(blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nome_usuario"]

    def save(self, *args, **kwargs):
        if not self.nome_usuario and self.email:
            self.nome_usuario = self.email.split("@")[0]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email


class Pessoa(models.Model):
    id = models.BigAutoField(primary_key=True)
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    nome_completo = models.CharField(max_length=150)
    cpf = models.CharField(max_length=14, unique=True)
    data_nascimento = models.DateField()
    telefone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Endereco(models.Model):
    id = models.BigAutoField(primary_key=True)
    usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, related_name="enderecos"
    )
    tipo = models.CharField(max_length=20, choices=TipoEndereco.choices)
    logradouro = models.CharField(max_length=150)
    numero = models.CharField(max_length=20)
    complemento = models.CharField(max_length=100, blank=True)
    cep = models.CharField(max_length=15)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=50)
