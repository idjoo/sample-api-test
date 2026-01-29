from .base_exception import BaseError


class SampleNotFoundError(BaseError):
    def __init__(self):
        super().__init__(status_code=404, message="Sample Not Found")


class SampleAlreadyExistsError(BaseError):
    def __init__(self):
        super().__init__(status_code=409, message="Sample Already Exists")
