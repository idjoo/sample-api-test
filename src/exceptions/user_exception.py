from .base_exception import BaseError


class UserNotFoundError(BaseError):
    def __init__(self):
        super().__init__(status_code=404, message="User Not Found")


class UserAlreadyExistsError(BaseError):
    def __init__(self):
        super().__init__(status_code=409, message="User Already Exists")


class InvalidCredentialsError(BaseError):
    def __init__(self):
        super().__init__(status_code=401, message="Invalid Credentials")


class UnauthorizedError(BaseError):
    def __init__(self):
        super().__init__(status_code=401, message="Unauthorized")


class ForbiddenError(BaseError):
    def __init__(self):
        super().__init__(status_code=403, message="Forbidden")
