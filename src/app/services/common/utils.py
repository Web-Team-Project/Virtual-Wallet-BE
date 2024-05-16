from typing import Callable, Any
from fastapi.responses import JSONResponse
from fastapi import status
import logging
from response import WebErrorResponse
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


async def process_request(execute_fn: Callable) -> Any | JSONResponse:
    try:
        return await execute_fn()
    except SQLAlchemyError as ex:
        logger.exception("Database.....")
        return WebErrorResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ex,
        )
    except SyntaxError as ex:
        logger.exception("Syntax Error")
        return WebErrorResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ex,
        )