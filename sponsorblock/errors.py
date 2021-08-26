class InvalidJSONException(Exception):
    """Raised when the JSON gotten from the server is invalid"""

    def __init__(self, message, response):
        self.response = response
        super().__init__(f"{message}: {response.text}")


class HTTPException(Exception):
    """Raised when the server returns an error code"""

    def __init__(self, message, response):
        self.response = response
        super().__init__(f"{message}: {response.status_code} {response.reason}")


class Forbidden(HTTPException):
    """Raised if the status code is 403"""


class BadRequest(HTTPException):
    """Raised if the status code is 400"""


class NotFoundException(HTTPException):
    """Raised when the status code is 404"""


class RateLimitException(HTTPException):
    """Raised when the status code is 429"""


class UnexpectedException(HTTPException):
    """Raised if an unknown error has occurred."""


class ServerException(HTTPException):
    """Raised if the status code is bigger than 500"""


class DuplicateException(HTTPException):
    """Raised if the status code is 409"""
