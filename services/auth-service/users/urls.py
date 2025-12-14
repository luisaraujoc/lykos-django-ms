from posixpath import basename
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, LoginView, MeView, PessoaViewSet, EnderecoViewSet

router = DefaultRouter()
router.register(r'pessoas', PessoaViewSet, basename='pessoas')
router.register(r'enderecos', EnderecoViewSet, basename='enderecos')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('me/', MeView.as_view(), name='me'),
    path('', include(router.urls)),
]