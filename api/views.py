from django.http import JsonResponse
from .predict_model import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from .models import UploadedFile
from .serializers import UploadedFileSerializer
from helper.types import ResponseData


def simple_api(request):
    media_url = request.GET.get('url')
    response = predict_video(media_url)
    response_data = ResponseData(status="success", code=200, message="Prediction successful", data=response, error=None)
    return response_data.build_response()


class FileUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        serializer = UploadedFileSerializer(data=request.data)
        if not serializer.is_valid():
            response_data = ResponseData(
                status="error",
                code=400,
                message="Bad Request",
                data=None,
                error=serializer.errors
            )
            return response_data.build_response()
        
        try:
            uploaded_file: UploadedFile = serializer.save()
            response = predict_video(uploaded_file.get_absolute_path())
            response_data = ResponseData(
                status="success",
                code=200,
                message="Prediction completed",
                data=response,
                error=None
            )
            return response_data.build_response()
        except Exception as e:
            response_data = ResponseData(
                status="error",
                code=500,
                message="An error occurred",
                data=None,
                error=str(e)
            )
            return response_data.build_response()