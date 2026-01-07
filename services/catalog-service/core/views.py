from rest_framework import viewsets, permissions
from .models import Categoria, Pacote
from .serializers import CategoriaSerializer, PacoteSerializer

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    # Permite leitura para todos, escrita só para admin (ajustar conforme necessidade)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class PacoteViewSet(viewsets.ModelViewSet):
    queryset = Pacote.objects.all()
    serializer_class = PacoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Isso é para filtrar apenas os pacotes do usuário logado na rota "meus pacotes":
        # Mas no catálogo geral, queremos ver todos.
        # Vamos manter padrão (vê tudo) por enquanto.
        return Pacote.objects.all().order_by('-data_criacao')

    def perform_create(self, serializer):
        user_id = self.request.headers.get('X-User-Id')
        
        # Se não tiver header (teste local direto), usa 1 provisório
        if not user_id:
            user_id = 1 
            
        serializer.save(freelancer_id=user_id)