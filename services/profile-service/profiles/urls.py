from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TornarSeFreelancerView,
    PortfolioViewSet,
    FreelancerMeView,
    IdiomaViewSet,
    HabilidadeViewSet
)

# Roteador para ViewSets (CRUDs automáticos)
router = DefaultRouter()
router.register(r'portfolio', PortfolioViewSet, basename='portfolio')
router.register(r'idiomas', IdiomaViewSet, basename='idiomas')
router.register(r'habilidades', HabilidadeViewSet, basename='habilidades')

urlpatterns = [
    # Rotas de APIViews (Manuais)
    path('become-freelancer/', TornarSeFreelancerView.as_view(), name='become-freelancer'),
    path('me/', FreelancerMeView.as_view(), name='freelancer-me'),

    # Rotas do Router (tem que vir por último para não engolir as outras)
    path('', include(router.urls)),
]