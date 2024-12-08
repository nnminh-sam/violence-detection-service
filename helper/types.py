from datetime import datetime
from django.http import JsonResponse


class ResponseData:
    def __init__(self, status, code, message, data, error):
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.status = status
        self.code = code
        self.message = message
        self.data = data
        self.error = error

    def build_response(self):
        response_content = {
            "status": self.status,
            "message": self.message,
            "data": self.data,
            "error": self.error
        }
        return JsonResponse(response_content)