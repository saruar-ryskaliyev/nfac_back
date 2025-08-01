from typing import Any, Dict, Union, Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.schemas.message import ErrorResponse

ERROR_RESPONSES: Dict[Union[int, str], Dict[str, Any]] = {
    status.HTTP_400_BAD_REQUEST: {
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {
                    "app_exception": "Response4XX",
                    "context": {"reason": "client error"},
                }
            }
        },
    },
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {
                    "app_exception": "Response5XX",
                    "context": {"error": "server error"},
                }
            }
        },
    },
}


class AppExceptionCase(Exception):
    def __init__(self, status_code: int, context: dict):
        self.exception_case = self.__class__.__name__
        self.status_code = status_code
        self.context = context

    def __str__(self):
        return f"<AppException {self.exception_case}> - " + f"status_code={self.status_code} - context={self.context}>"


async def app_exception_handler(request: Request, exc: AppExceptionCase):
    return JSONResponse(
        status_code=exc.status_code,
        content={"app_exception": exc.exception_case, "context": exc.context},
    )


class AppException:
    class Response4XX(AppExceptionCase):
        """
        4xx error
        """
        def __init__(
            self,
            status_code: int = status.HTTP_400_BAD_REQUEST,
            context: Optional[Dict[str, Any]] = None,
        ):
            # now both the annotation and the default are ints
            super().__init__(status_code, context or {})

    class Response5XX(AppExceptionCase):
        """
        5xx error
        """
        def __init__(
            self,
            status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
            context: Optional[Dict[str, Any]] = None,
        ):
            super().__init__(status_code, context or {})


response_4xx = AppException.Response4XX
response_5xx = AppException.Response5XX
