from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Vamos incluir as rotas do app profiles (criaremos o urls.py dele em breve)
    # Por enquanto, se o app profiles não tiver urls.py, comente a linha abaixo:
    # path('api/profiles/', include('profiles.urls')),

    # Documentação Swagger
    path('api/profiles/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/profiles/schema/docs/', SpectacularSwaggerView.as_view(url_name='schema')),
]