class InvalidJSONError(Exception):
    """Raised when the JSON gotten from the server is invalid"""
    def __init__(self, message, response):
        self.response = response
        super().__init__(message + ': ' + response.text)

class HTTPException(Exception):
    """Raised when the server returns an error code"""
    def __init__(self, message, response):
        self.response = response
        super().__init__(message + ': ' + response.status_code + response.reason)
