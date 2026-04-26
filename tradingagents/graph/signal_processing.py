# TradingAgents/graph/signal_processing.py

from langchain_openai import ChatOpenAI


class SignalProcessor:
    """Processes trading signals to extract actionable decisions."""

    def __init__(self, quick_thinking_llm: ChatOpenAI):
        """Initialize with an LLM for processing."""
        self.quick_thinking_llm = quick_thinking_llm

    def process_signal(self, full_signal: str) -> str:
        """
        Process a full trading signal to extract the core decision and confidence.

        Args:
            full_signal: Complete trading signal text

        Returns:
            Extracted decision with confidence (e.g., "BUY 85%")
        """
        messages = [
            (
                "system",
                "You are an efficient assistant designed to analyze paragraphs or "
                "financial reports provided by a group of analysts. Your task is to "
                "extract the investment decision (BUY, SELL, or HOLD) and the "
                "confidence percentage. Output ONLY in this exact format: "
                "DECISION XX% (e.g., 'BUY 85%' or 'SELL 60%' or 'HOLD 45%'). "
                "If no confidence percentage is explicitly stated, estimate one "
                "based on the conviction and certainty expressed in the text. "
                "Do not add any other text.",
            ),
            ("human", full_signal),
        ]

        return self.quick_thinking_llm.invoke(messages).content
