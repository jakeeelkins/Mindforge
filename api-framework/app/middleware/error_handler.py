from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from fastapi import status

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)

        # Handle FastAPI/Starlette HTTP exceptions (e.g. 404)
        except StarletteHTTPException as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "error": exc.detail if exc.detail else "HTTP Error",
                    "message": str(exc.detail),
                    "path": request.url.path,
                },
            )

        # Handle request validation errors (422)
        except RequestValidationError as exc:
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    "error": "Validation Error",
                    "message": exc.errors(),
                    "path": request.url.path,
                },
            )

        # Handle all other exceptions (500)
        except Exception as exc:
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "message": str(exc),
                    "path": request.url.path,
                },
            )
