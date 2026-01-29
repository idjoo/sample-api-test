from .base_exception import BaseError


class ItemNotFoundError(BaseError):
    def __init__(self):
        super().__init__(status_code=404, message="Item Not Found")


class ItemAlreadyExistsError(BaseError):
    def __init__(self):
        super().__init__(status_code=409, message="Item Already Exists")
