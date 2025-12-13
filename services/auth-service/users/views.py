from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UsuarioSerializer, RegisterSerializer, PessoaSerializer, EnderecoSerializer, CustomTokenObtainPairSerializer
from .models import Usuario, Pessoa, Endereco

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Usuário criado'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Usa headers do Traefik se disponível, senão request.user
        user_id = request.headers.get('X-User-Id', request.user.id)
        user = Usuario.objects.get(id=user_id)
        serializer = UsuarioSerializer(user)
        return Response(serializer.data)

class PessoaViewSet(viewsets.ModelViewSet):
    serializer_class = PessoaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Pessoa.objects.filter(usuario_id=self.request.headers.get('X-User-Id'))

class EnderecoViewSet(viewsets.ModelViewSet):
    serializer_class = EnderecoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Endereco.objects.filter(usuario_id=self.request.headers.get('X-User-Id'))

    def perform_create(self, serializer):
        serializer.save(usuario_id=self.request.headers.get('X-User-Id'))