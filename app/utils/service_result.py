from fastapi import HTTPException
from fastapi.responses import JSONResponse
from loguru import logger
from typing import Any, Callable
from functools import wraps
from app.utils import AppExceptionCase, response_5xx

class ServiceResult:
    def __init__(self, payload: Any):
        """
        payload is either:
          - AppExceptionCase: a known business error
          - any other object: the “good” result
        """
        if isinstance(payload, AppExceptionCase):
            self.success = False
            self.error = payload
        else:
            self.success = True
            self.value = payload

    async def unwrap(self):
        """
        If error → log & raise HTTPException.
        If success → return the raw data (not a JSONResponse).
        """
        if not self.success:
            # Log it
            logger.error(f"{self.error} in service")
            # Turn it into an HTTP exception
            raise HTTPException(
                status_code=self.error.status_code,
                detail=self.error.exception_case,
            )
        return self.value


def return_service(func: Callable) -> Callable:
    """
    Decorator that wraps service functions to return ServiceResult objects.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
            return ServiceResult(result)
        except Exception as e:
            if isinstance(e, AppExceptionCase):
                return ServiceResult(e)
            # Convert unexpected exceptions to a generic error
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
            return ServiceResult(response_5xx())
    return wrapper


async def handle_result(service_result: ServiceResult) -> JSONResponse:
    """
    Handle a ServiceResult and return appropriate JSONResponse.
    """
    if service_result.success:
        return JSONResponse(content=service_result.value, status_code=200)
    else:
        return JSONResponse(
            content={"detail": service_result.error.exception_case},
            status_code=service_result.error.status_code
        )
