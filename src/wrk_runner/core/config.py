from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


class TestConfig(BaseModel):
    name: str = Field(..., description="Test identifier")
    url: str = Field(..., description="URL to test")
    duration: Optional[int] = None
    connections: Optional[int] = None
    threads: Optional[int] = None
    warmup: Optional[int] = None
    lua_script: Optional[str] = None


class Config(BaseModel):
    duration: int = Field(default=30, description="Test duration in seconds")
    connections: int = Field(default=1000, description="Number of connections")
    threads: int = Field(default=8, description="Number of threads")
    warmup: int = Field(default=5, description="Warmup time in seconds")
    output_dir: str = Field(default="results", description="Output directory")
    lua_script: Optional[str] = Field(None, description="Lua script for wrk")
    generate_html_report: bool = Field(default=True, description="Generate HTML report")
    generate_json_export: bool = Field(default=True, description="Generate JSON export")
    chart_format: str = Field(
        default="html", description="Chart format: html, json, rich"
    )
    tests: List[TestConfig] = Field(..., description="List of tests to run")

    @validator("output_dir")
    def validate_output_dir(cls, v: str) -> str:
        Path(v).mkdir(parents=True, exist_ok=True)
        return v

    def get_test_config(self, test: TestConfig) -> Dict[str, Any]:
        config = self.dict()
        for field in ["duration", "connections", "threads", "warmup", "lua_script"]:
            test_value = getattr(test, field)
            if test_value is not None:
                config[field] = test_value
        return config
