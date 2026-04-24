from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class RAREventModel(Base):
    __tablename__ = "rar_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    cell_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    ta: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    ue_temp_id: Mapped[str | None] = mapped_column(String, nullable=True)
    request_type: Mapped[str | None] = mapped_column(String, nullable=True)
    result: Mapped[str | None] = mapped_column(String, nullable=True)
    event_type: Mapped[str | None] = mapped_column(String, nullable=True)

class KPIProfileModel(Base):
    __tablename__ = "kpi_profile"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cell_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    ta: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    time_bucket: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    window_sec: Mapped[int] = mapped_column(Integer, nullable=False)
    mu: Mapped[float] = mapped_column(Float, nullable=False)
    sigma: Mapped[float] = mapped_column(Float, nullable=False)
    samples: Mapped[int] = mapped_column(Integer, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

class AlarmModel(Base):
    __tablename__ = "alarms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    cell_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    ta: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    observed_x: Mapped[float] = mapped_column(Float, nullable=False)
    mu: Mapped[float] = mapped_column(Float, nullable=False)
    sigma: Mapped[float] = mapped_column(Float, nullable=False)
    anomaly_score: Mapped[float] = mapped_column(Float, nullable=False)
    threshold: Mapped[float] = mapped_column(Float, nullable=False)
    action: Mapped[str] = mapped_column(String, nullable=False)

class PolicyModel(Base):
    __tablename__ = "policies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    cell_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    ta: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    policy_type: Mapped[str] = mapped_column(String, nullable=False)
    duration_sec: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False)

class RuntimeConfigModel(Base):
    __tablename__ = "runtime_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    threshold: Mapped[float] = mapped_column(Float, nullable=False)
    sigma_floor: Mapped[float] = mapped_column(Float, nullable=False)
    persistence_windows: Mapped[int] = mapped_column(Integer, nullable=False)
    block_duration_sec: Mapped[int] = mapped_column(Integer, nullable=False)
    neighbor_ta_span: Mapped[int] = mapped_column(Integer, nullable=False)
    action_ladder: Mapped[str] = mapped_column(Text, nullable=False)