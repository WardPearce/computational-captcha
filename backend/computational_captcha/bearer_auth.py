import base64
import binascii
import secrets

from computational_captcha.env import SETTINGS
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, hmac
from litestar.connection import ASGIConnection
from litestar.exceptions import NotAuthorizedException
from litestar.middleware.authentication import (
    AbstractAuthenticationMiddleware,
    AuthenticationResult,
)

API_KEY_HEADER = "Authorization"


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

        key = secrets.token_bytes()

        given_password = hmac.HMAC(key, hashes.SHA256())
        given_password.update(password.encode())

        correct_password = hmac.HMAC(key, hashes.SHA256())
        correct_password.update(SETTINGS.captcha.api_key.encode())

        try:
            correct_password.verify(given_password.finalize())
        except InvalidSignature:
            raise NotAuthorizedException()

        return AuthenticationResult(user=username, auth=password)
