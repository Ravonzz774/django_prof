import random
import string

from django.http import JsonResponse
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.views import exception_handler, APIView


def generateFileId(number = 10):
    allSymbols = string.ascii_letters + string.digits
    return ''.join(random.choice(allSymbols) for _ in range(number))



def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    print(exc.get_codes())
    if response is not None:
        code = exc.get_codes()
        if code in ["not_authenticated", "authentication_failed"]:
            response.data = {
                "message": "Login failed"
            }
            response.status_code = 403

        if code in ["not_found"]:
            response.data = {
                "message": "Not found"
            }

        if code in ['permission_denied']:
            response.data = {
                "message": "Forbidden for you"
            }
            response.status_code = 403

    return response


def custom404view(request, exception):
    response = JsonResponse({"message": "Not found"}, status=404)
    return response