"""SQLAlchemy ORM models for the TradingAgents application."""

import uuid
from datetime import datetime, date

from sqlalchemy import (
    String,
    Text,
    Float,
    Integer,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    JSON,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def _generate_uuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    return datetime.utcnow()


class Base(DeclarativeBase):
    pass


class AnalysisSession(Base):
    __tablename__ = "analysis_sessions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=_generate_uuid
    )
    ticker: Mapped[str] = mapped_column(String(10), nullable=False)
    market_id: Mapped[str] = mapped_column(String(20), nullable=False)
    analysis_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending"
    )  # pending, running, completed, failed, cancelled
    trade_horizon: Mapped[str] = mapped_column(String(20), nullable=False)
    research_depth: Mapped[str] = mapped_column(String(20), nullable=False)
    analysts: Mapped[list] = mapped_column(JSON, nullable=False)
    llm_provider: Mapped[str] = mapped_column(String(50), nullable=False)
    quick_think_model: Mapped[str] = mapped_column(String(100), nullable=False)
    deep_think_model: Mapped[str] = mapped_column(String(100), nullable=False)
    recommendation: Mapped[str | None] = mapped_column(String(10), nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    reports_path: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    stock_name: Mapped[str] = mapped_column(String(200), nullable=False, default="")
    stock_price_at_analysis: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )
    language: Mapped[str] = mapped_column(String(5), nullable=False, default="en")
    engine_scores: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    tags: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    # Relationships
    agent_reports: Mapped[list["AgentReport"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )
    simulation_result: Mapped["SimulationResult | None"] = relationship(
        back_populates="session", uselist=False, cascade="all, delete-orphan"
    )


class AgentReport(Base):
    __tablename__ = "agent_reports"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=_generate_uuid
    )
    session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("analysis_sessions.id"), nullable=False
    )
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phase: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    session: Mapped["AnalysisSession"] = relationship(back_populates="agent_reports")


class SimulationResult(Base):
    __tablename__ = "simulation_results"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=_generate_uuid
    )
    session_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("analysis_sessions.id"),
        nullable=False,
        unique=True,
    )
    entry_price: Mapped[float] = mapped_column(Float, nullable=False)
    exit_price: Mapped[float] = mapped_column(Float, nullable=False)
    horizon_end_date: Mapped[date] = mapped_column(Date, nullable=False)
    return_pct: Mapped[float] = mapped_column(Float, nullable=False)
    is_win: Mapped[bool] = mapped_column(Boolean, nullable=False)
    simulated_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    # Relationships
    session: Mapped["AnalysisSession"] = relationship(
        back_populates="simulation_result"
    )


class Portfolio(Base):
    __tablename__ = "portfolios"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=_generate_uuid
    )
    starting_balance: Mapped[float] = mapped_column(Float, nullable=False, default=100000.0)
    cash_balance: Mapped[float] = mapped_column(Float, nullable=False, default=100000.0)
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="USD")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    reset_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    positions: Mapped[list["Position"]] = relationship(
        back_populates="portfolio", cascade="all, delete-orphan"
    )


class Position(Base):
    __tablename__ = "positions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=_generate_uuid
    )
    portfolio_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("portfolios.id"), nullable=False
    )
    analysis_session_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("analysis_sessions.id"), nullable=True
    )
    ticker: Mapped[str] = mapped_column(String(10), nullable=False)
    market_id: Mapped[str] = mapped_column(String(20), nullable=False)
    direction: Mapped[str] = mapped_column(String(10), nullable=False)  # long / short
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    entry_price: Mapped[float] = mapped_column(Float, nullable=False)
    entry_date: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    exit_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    exit_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(
        String(10), nullable=False, default="open"
    )  # open / closed
    realized_pnl: Mapped[float | None] = mapped_column(Float, nullable=True)
    realized_pnl_pct: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Relationships
    portfolio: Mapped["Portfolio"] = relationship(back_populates="positions")
    analysis_session: Mapped["AnalysisSession | None"] = relationship()


class EquitySnapshot(Base):
    __tablename__ = "equity_snapshots"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=_generate_uuid
    )
    portfolio_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("portfolios.id"), nullable=False
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    total_value: Mapped[float] = mapped_column(Float, nullable=False)
    cash_balance: Mapped[float] = mapped_column(Float, nullable=False)
    positions_value: Mapped[float] = mapped_column(Float, nullable=False)


class WatchlistItem(Base):
    __tablename__ = "watchlist_items"
    __table_args__ = (UniqueConstraint("ticker", "market_id", name="uq_watchlist_ticker_market"),)

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=_generate_uuid
    )
    ticker: Mapped[str] = mapped_column(String(10), nullable=False)
    market_id: Mapped[str] = mapped_column(String(20), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False, default="")
    added_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")


class UserSettings(Base):
    __tablename__ = "user_settings"

    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[str] = mapped_column(String(2000), nullable=False)
