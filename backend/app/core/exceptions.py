from fastapi import HTTPException, status


class AppHTTPException(HTTPException):
    def __init__(self, status_code: int, detail: str, error_code: str = "GENERIC_ERROR", headers: dict | None = None):
        super().__init__(status_code=status_code, detail={"message": detail, "error_code": error_code}, headers=headers)


AUTH_INVALID_CREDENTIALS = lambda: AppHTTPException(  # noqa: E731
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid email or password",
    error_code="AUTH_INVALID_CREDENTIALS",
)

AUTH_TOKEN_INVALID = lambda: AppHTTPException(  # noqa: E731
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    error_code="AUTH_TOKEN_INVALID",
    headers={"WWW-Authenticate": "Bearer"},
)

RESOURCE_CONFLICT = lambda msg: AppHTTPException(  # noqa: E731
    status_code=status.HTTP_409_CONFLICT,
    detail=msg,
    error_code="RESOURCE_CONFLICT",
)

RESOURCE_NOT_FOUND = lambda msg: AppHTTPException(  # noqa: E731
    status_code=status.HTTP_404_NOT_FOUND,
    detail=msg,
    error_code="RESOURCE_NOT_FOUND",
)

CART_EMPTY = lambda: AppHTTPException(  # noqa: E731
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Cart is empty",
    error_code="CART_EMPTY",
)
