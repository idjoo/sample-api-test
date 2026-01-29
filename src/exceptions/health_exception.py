from .base_exception import BaseError


class CacheHealthError(BaseError):
    def __init__(self):
        super().__init__(status_code=500, message="Cache Not Healthy")


class DatabaseHealthError(BaseError):
    def __init__(self):
        super().__init__(status_code=500, message="Database Not Healthy")
