from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


class WebErrorResponse(JSONResponse):
    """
    Error response returned by all ..... APIs endpoints.
    """

    def render(self, content: Any) -> bytes:
        """
        Override the render method of JSONResponse to
        always return the error message in specified format.
        """
        return super().render(jsonable_encoder({"detail": {"error": str(content)}}))
