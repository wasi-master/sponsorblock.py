from requests import Response

class InvalidJSONException(Exception):
    """Raised when the JSON gotten from the server is invalid"""

    def __init__(self, message, response):
        self.response = response
        super().__init__(f"{message}: {response.text}")


class HTTPException(Exception):
    """Raised when the server returns an error code"""

    def __init__(self, message, response: Response):
        self.response: Response = response
        super().__init__(f"{message}: {response.status_code} {response.reason} - {response.text}")

    def __str__(self):
        newline = "\n"

        return f"""
{super().__str__()}
{self.response.url} {self.response.url}
{newline.join(f'{key}: {value}' for key, value in self.response.request.headers.items())}
{self.response.content}
        """


class Forbidden(HTTPException):
    """Raised when the status code is 403."""


class BadRequest(HTTPException):
    """Raised when the status code is 400."""


class NotFoundException(HTTPException):
    """Raised when the status code is 404."""


class RateLimitException(HTTPException):
    """Raised when the status code is 429."""


class UnexpectedException(HTTPException):
    """Raised when an unknown error has occurred."""


class ServerException(HTTPException):
    """Raised if the status code is bigger than 500."""


class DuplicateException(HTTPException):
    """Raised when the status code is 409."""
