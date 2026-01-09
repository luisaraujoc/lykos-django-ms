from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import TornarSeFreelancerSerializer
from .models import Freelancer


class TornarSeFreelancerView(generics.CreateAPIView):
    """
    Endpoint para transformar o usuário logado em Freelancer.
    Recebe multipart/form-data com foto, dados e arrays de skills.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # Essencial para upload de arquivos
    serializer_class = TornarSeFreelancerSerializer

    def create(self, request, *args, **kwargs):
        # Passa o request no contexto para pegarmos o user.id
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        freelancer = serializer.save()

        return Response({
            "detail": "Perfil de freelancer criado com sucesso!",
            "id": freelancer.id,
            "nome": freelancer.nome_exibicao
        }, status=status.HTTP_201_CREATED)