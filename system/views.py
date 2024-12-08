from helper.types import ResponseData


def health_check(request):
    return ResponseData(
        data=None,
        status='Success',
        message='System is running',
        code=200,
    ).build_response()
