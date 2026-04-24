from datetime import datetime
from typing import Literal, Optional, List
from pydantic import BaseModel, Field

class RAREvent(BaseModel):
    timestamp: datetime
    cell_id: str
    event_type: str = "RAR"
    ta: int
    ue_temp_id: Optional[str] = None
    request_type: str = "connection_establish"
    result: str = "observed"

class SyntheticRequest(BaseModel):
    preset: Literal["simulation_clean", "simulation_attack", "simulation_mixed", "testbed_clean", "testbed_attack", "testbed_mixed"]
    cell_id: str = "cell_1"
    windows: int = 60
    window_sec: int = 60
    base_ta: int = 77
    start_time: Optional[datetime] = None
    seed: int = 42

class ConfigUpdateRequest(BaseModel):
    threshold: Optional[float] = None
    sigma_floor: Optional[float] = None
    persistence_windows: Optional[int] = None
    block_duration_sec: Optional[int] = None
    neighbor_ta_span: Optional[int] = None
    action_ladder: Optional[List[float]] = Field(default=None, description="Three ascending thresholds: alert, rate_limit, reject")

class TrainResponse(BaseModel):
    windows_processed: int
    profiles_written: int

class InferResponse(BaseModel):
    windows_processed: int
    alarms: int
    policies: int

class AlarmOut(BaseModel):
    id: int
    ts: datetime
    cell_id: str
    ta: int
    observed_x: float
    mu: float
    sigma: float
    anomaly_score: float
    threshold: float
    action: str

class PolicyOut(BaseModel):
    id: int
    created_at: datetime
    cell_id: str
    ta: int
    policy_type: str
    duration_sec: Optional[int]
    status: str

class ProfileOut(BaseModel):
    cell_id: str
    ta: int
    time_bucket: int
    window_sec: int
    mu: float
    sigma: float
    samples: int
