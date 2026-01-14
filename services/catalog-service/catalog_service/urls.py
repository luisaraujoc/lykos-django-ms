from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from core.views import CategoriaViewSet, PacoteViewSet

# Cria as rotas automáticas (/categorias/, /pacotes/)
router = DefaultRouter()
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'pacotes', PacoteViewSet, basename='pacote')

urlpatterns = [
    path('admin/', admin.site.urls),
    # Rotas da API
    path('api/catalog/', include(router.urls)),
    
    # Swagger
    path('api/catalog/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/catalog/schema/docs/', SpectacularSwaggerView.as_view(url_name='schema')),
]