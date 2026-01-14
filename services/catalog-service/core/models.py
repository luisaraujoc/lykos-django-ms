from django.db import models
from shared.enums import StatusPacote  # temido shared do projeto, viu sacana!!!
from shared.constants import MAX_PACOTE_REVISOES

class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icone = models.CharField(max_length=50, blank=True, help_text="Classe do ícone (ex: fa-camera)")
    ativa = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

class Pacote(models.Model):
    # Temidos Relacionamentos
    categoria = models.ForeignKey(Categoria, related_name='pacotes', on_delete=models.CASCADE)
    
    # Identificação do Freelancer (Apenas o ID, pois o usuário está no auth-service)
    freelancer_id = models.BigIntegerField(db_index=True)
    
    # Dados do Pacote
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    prazo_entrega_dias = models.PositiveIntegerField()
    qtd_revisoes = models.PositiveIntegerField(default=1)
    
    # Imagem de capa (URL ou caminho)
    capa = models.ImageField(upload_to='pacotes/capas/', blank=True, null=True)
    
    # Controle
    status = models.CharField(
        max_length=20, 
        choices=StatusPacote.choices, 
        default=StatusPacote.ATIVO
    )
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.titulo} - R$ {self.preco}"