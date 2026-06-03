from fastapi import HTTPException, status


class BaseHTTPException(HTTPException):
    def __init__(self, detail: str = None):
        super().__init__(status_code=self.status_code, detail=detail or self.default_detail)


class UserAlreadyExistsError(BaseHTTPException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "User already exists"


class InvalidCredentialsError(BaseHTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Invalid credentials"


class InvalidTokenError(BaseHTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Invalid token"


class TokenExpiredError(BaseHTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Token has expired"


class UserNotFoundError(BaseHTTPException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "User not found"
