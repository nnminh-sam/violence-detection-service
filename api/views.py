from django.http import JsonResponse
from .predict_model import *


def simple_api(request):
    media_url = request.GET.get('url')
    response = predict_video(media_url)
    return JsonResponse(response)