from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "sqlite:///./ssd_xapp.db"
    redis_url: str = "redis://localhost:6379/0"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    default_threshold: float = 1.0
    default_sigma_floor: float = 0.5
    default_persistence_windows: int = 2
    default_block_duration_sec: int = 300
    default_neighbor_ta_span: int = 1
    live_poll_batch: int = 500

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
