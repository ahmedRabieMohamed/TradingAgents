"""TradingAgents backend application package."""

import os
import sys

# Ensure the parent project's `tradingagents` package is importable when the
# backend is started from the backend/ directory.
_PARENT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _PARENT_DIR not in sys.path:
    sys.path.insert(0, _PARENT_DIR)
