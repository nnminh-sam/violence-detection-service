from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import simple_api
from .views import FileUploadView


urlpatterns = [
    path('v1/predict/', simple_api, name='simple_api'),
    path('v2/predict/', FileUploadView.as_view(), name='file-upload'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)