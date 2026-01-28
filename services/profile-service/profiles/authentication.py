from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from types import SimpleNamespace
import logging

logger = logging.getLogger(__name__)


class StatelessJWTAuthentication(JWTAuthentication):
    """
    Autenticação JWT Stateless com Logs de Debug.
    """

    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            print("🔴 DEBUG AUTH: Header 'Authorization' não encontrado.")
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            print("🔴 DEBUG AUTH: Token raw não encontrado.")
            return None

        try:
            # Tenta validar a assinatura usando a SECRET_KEY do settings.py
            validated_token = self.get_validated_token(raw_token)
            print(f"🟢 DEBUG AUTH: Token validado! Payload: {validated_token}")
        except Exception as e:
            # AQUI ESTÁ O ERRO 401
            print(f"🔴 DEBUG AUTH: Erro na validação do token: {e}")
            print(f"🔴 DEBUG AUTH: Verifique se a SECRET_KEY no .env é IGUAL à do Auth Service.")
            raise InvalidToken(e)

        return self.get_user(validated_token), validated_token

    def get_user(self, validated_token):
        try:
            user_id = validated_token.get('user_id')
            print(f"🟢 DEBUG AUTH: User ID extraído do token: {user_id}")
        except KeyError:
            raise InvalidToken("Token sem user_id")

        if not user_id:
            raise InvalidToken("Token sem user_id válido")

        # Cria usuário em memória
        user = SimpleNamespace()
        user.id = user_id
        user.pk = user_id
        user.is_authenticated = True
        user.is_anonymous = False
        user.username = f"user_{user_id}"

        return user