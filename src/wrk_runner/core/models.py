from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ServerMetrics(BaseModel):
    requests_per_sec: Optional[float] = None
    transfer_per_sec: Optional[str] = None
    latency_50: Optional[str] = None
    latency_75: Optional[str] = None
    latency_90: Optional[str] = None
    latency_99: Optional[str] = None
    total_requests: Optional[int] = None
    total_errors: Optional[int] = None
    raw_output: Optional[str] = None

    class Config:
        extra = "allow"


class TestResult(BaseModel):
    server: str = Field(..., description="Server/test identifier")
    url: str = Field(..., description="Tested URL")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    duration: int = Field(..., description="Test duration in seconds")
    connections: int = Field(..., description="Number of connections")
    threads: int = Field(..., description="Number of threads")
    metrics: ServerMetrics = Field(default_factory=ServerMetrics)
    config: Dict[str, Any] = Field(default_factory=dict)
    output_file: Optional[str] = None
    json_file: Optional[str] = None

    class Config:
        extra = "allow"
