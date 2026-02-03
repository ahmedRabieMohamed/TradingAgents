import unittest

from tradingagents.api.deps.errors import ApiError
from tradingagents.api.routers.symbols import _resolve_search_query


class TestResolveSearchQuery(unittest.TestCase):
    def test_prefers_query_param(self) -> None:
        self.assertEqual(_resolve_search_query("A", None), "A")

    def test_falls_back_to_q_param(self) -> None:
        self.assertEqual(_resolve_search_query(None, "MSFT"), "MSFT")

    def test_missing_params_raises_validation_error(self) -> None:
        with self.assertRaises(ApiError) as context:
            _resolve_search_query(None, None)

        exc = context.exception
        self.assertEqual(exc.status_code, 422)
        self.assertEqual(exc.code, "VALIDATION_ERROR")


if __name__ == "__main__":
    unittest.main()
