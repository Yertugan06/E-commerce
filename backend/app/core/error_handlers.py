from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


async def app_http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    content = exc.detail if isinstance(exc.detail, dict) else {"message": exc.detail, "error_code": "GENERIC_ERROR"}
    if "detail" not in content:
        content["detail"] = content.get("message", "")
    return JSONResponse(
        status_code=exc.status_code,
        content=content,
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = []
    for err in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in err["loc"]),
            "message": err["msg"],
            "type": err["type"],
        })
    return JSONResponse(
        status_code=422,
        content={"message": "Validation failed", "error_code": "VALIDATION_ERROR", "errors": errors},
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error", "error_code": "INTERNAL_ERROR"},
    )
