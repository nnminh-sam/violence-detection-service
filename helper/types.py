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
        if self.data is not None:
            return JsonResponse({
                "status": self.status,
                "message": self.message,
                "data": JsonResponse(data=self.data, safe=False)
            })

        return JsonResponse({
            "status": self.status,
            "message": self.message,
            "error": self.error
        })