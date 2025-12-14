from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/auth/', include('dj_rest_auth.urls')),                    # login, logout, refresh
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),  # register + social
    path('api/auth/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/auth/schema/docs/', SpectacularSwaggerView.as_view(url_name='schema')),
]