from django.urls import path
from .views import TornarSeFreelancerView

urlpatterns = [
    path('become-freelancer/', TornarSeFreelancerView.as_view(), name='become-freelancer'),
]