import json
import unittest

from starlette.exceptions import HTTPException
from starlette.requests import Request

from tradingagents.api.deps.errors import http_exception_handler


class TestHttpExceptionHandler(unittest.IsolatedAsyncioTestCase):
    async def test_rate_limit_http_exception_maps_code(self) -> None:
        scope = {
            "type": "http",
            "method": "GET",
            "path": "/",
            "headers": [],
        }
        request = Request(scope)
        exc = HTTPException(status_code=429, detail="Too Many Requests")

        response = await http_exception_handler(request, exc)

        payload = json.loads(response.body.decode("utf-8"))

        self.assertEqual(response.status_code, 429)
        self.assertEqual(payload["error"]["code"], "RATE_LIMIT_EXCEEDED")


if __name__ == "__main__":
    unittest.main()
