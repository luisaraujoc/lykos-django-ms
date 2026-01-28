from rest_framework import viewsets, generics, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .serializers import TornarSeFreelancerSerializer
from .authentication import StatelessJWTAuthentication

from .models import Freelancer, PortfolioItem, Idioma, Habilidade
from .serializers import (
    TornarSeFreelancerSerializer,
    PortfolioItemSerializer,
    FreelancerSerializer,
    IdiomaSerializer,
    HabilidadeSerializer
)


class TornarSeFreelancerView(APIView):
    """
    Endpoint para criar/atualizar perfil de vendedor.
    Recebe Multipart Form Data (Arquivo + Dados).
    """
    authentication_classes = [StatelessJWTAuthentication]
    permission_classes = [IsAuthenticated]  # Exige token válido
    parser_classes = (MultiPartParser, FormParser)  # Crucial para receber a imagem

    def post(self, request, *args, **kwargs):
        # Passa o request no context para pegarmos o user.id dentro do serializer
        serializer = TornarSeFreelancerSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FreelancerMeView(generics.RetrieveAPIView):
    authentication_classes = [StatelessJWTAuthentication]
    serializer_class = FreelancerSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Retorna o perfil do usuário logado
        return Freelancer.objects.get(id=self.request.user.id)


class IdiomaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Idioma.objects.all().order_by('nome')
    serializer_class = IdiomaSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    filter_backends = [filters.SearchFilter]
    search_fields = ['nome', 'iso_codigo']


class HabilidadeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Habilidade.objects.all().order_by('nome')
    serializer_class = HabilidadeSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    filter_backends = [filters.SearchFilter]
    search_fields = ['nome']

class PortfolioViewSet(viewsets.ModelViewSet):
    authentication_classes = [StatelessJWTAuthentication]
    serializer_class = PortfolioItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PortfolioItem.objects.filter(project__freelancer__id=self.request.user.id)