import base64
import binascii

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError
from computational_captcha.env import SETTINGS
from litestar.connection import ASGIConnection
from litestar.exceptions import NotAuthorizedException
from litestar.middleware.authentication import (
    AbstractAuthenticationMiddleware,
    AuthenticationResult,
)

API_KEY_HEADER = "Authorization"
# Not used for password storage, just to help against timing attacks.
PASSWORD_HASHER = PasswordHasher(memory_cost=100)
HASHED_API_KEY = PASSWORD_HASHER.hash(SETTINGS.captcha.api_key)


class BearerAuthentication(AbstractAuthenticationMiddleware):
    async def authenticate_request(
        self, connection: ASGIConnection
    ) -> AuthenticationResult:
        if API_KEY_HEADER not in connection.headers:
            raise NotAuthorizedException()

        bearer_token = connection.headers[API_KEY_HEADER]

        try:
            scheme, credentials = bearer_token.split()
            if scheme.lower() != "basic":
                raise NotAuthorizedException()
            decoded = base64.b64decode(credentials).decode("ascii")
        except (ValueError, UnicodeDecodeError, binascii.Error):
            raise NotAuthorizedException()

        username, _, password = decoded.partition(":")

        try:
            PASSWORD_HASHER.verify(HASHED_API_KEY, password)
        except VerificationError:
            raise NotAuthorizedException()

        return AuthenticationResult(user=username, auth=password)
