from rest_framework.exceptions import APIException
from rest_framework import status

class NotFoundException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Recurso não encontrado'

class ConflictException(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Conflito de dados'

class UnauthorizedException(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Não autorizado'