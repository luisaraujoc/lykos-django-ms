from django.db import models
from django.utils.translation import gettext_lazy as _
from shared.enums import NivelIdioma, StatusPerfil


def freelancer_directory_path(instance, filename):
    return 'freelancers/user_{0}/{1}'.format(instance.id, filename)


class Freelancer(models.Model):
    id = models.BigIntegerField(primary_key=True, editable=False)
    nome_exibicao = models.CharField(max_length=150, blank=True)
    foto_perfil = models.ImageField(upload_to=freelancer_directory_path, blank=True, null=True)
    bio = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=StatusPerfil.choices, default=StatusPerfil.ATIVO)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Freelancer #{self.id} - {self.nome_exibicao}"


class Habilidade(models.Model):
    # Vamos popular via Seed
    nome = models.CharField(max_length=100, unique=True)
    freelancers = models.ManyToManyField(Freelancer, related_name='habilidades', blank=True)

    def __str__(self):
        return self.nome


class Idioma(models.Model):
    # Tabela de referência (Seedada + Cacheada)
    nome = models.CharField(max_length=50)
    iso_codigo = models.CharField(max_length=10, unique=True)  # Ex: PT_BR, EN_US

    def __str__(self):
        return f"{self.nome} ({self.iso_codigo})"


class FreelancerIdioma(models.Model):
    # Tabela associativa: O freelancer fala "Inglês" no nível "Fluente"
    freelancer = models.ForeignKey(Freelancer, on_delete=models.CASCADE, related_name='idiomas')
    idioma = models.ForeignKey(Idioma,
                               on_delete=models.PROTECT)  # Se apagar o idioma, não apaga o histórico? Melhor PROTECT.
    nivel = models.CharField(max_length=20, choices=NivelIdioma.choices)

    class Meta:
        unique_together = ('freelancer', 'idioma')


class Formacao(models.Model):
    # Relação 1:N (Um freelancer tem várias formações)
    freelancer = models.ForeignKey(Freelancer, on_delete=models.CASCADE, related_name='formacoes')
    titulo = models.CharField(max_length=200)
    instituicao = models.CharField(max_length=200)
    ano_conclusao = models.CharField(max_length=4)

    def __str__(self):
        return f"{self.titulo} - {self.instituicao}"