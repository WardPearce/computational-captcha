from litestar.exceptions import NotFoundException, PermissionDeniedException


class CaptchaNotFoundError(NotFoundException):
    def __init__(
        self,
    ) -> None:
        super().__init__(detail="Captcha ID not found.")


class CaptchaComputedInvalidError(PermissionDeniedException):
    def __init__(
        self,
    ) -> None:
        super().__init__(detail="Provided computed hash is invalid.")
