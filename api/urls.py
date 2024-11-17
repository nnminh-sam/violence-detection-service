from django.urls import path
from .views import simple_api

urlpatterns = [
    path('v1/predict/', simple_api, name='simple_api'),
]