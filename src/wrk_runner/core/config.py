"""Configuration models for wrk-runner."""

from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


class TestConfig(BaseModel):
    """Configuration for a single test."""

    name: str = Field(..., description="Test identifier")
    url: str = Field(..., description="URL to test")

    # Optional overrides
    duration: Optional[int] = None
    connections: Optional[int] = None
    threads: Optional[int] = None
    warmup: Optional[int] = None
    lua_script: Optional[str] = None


class Config(BaseModel):
    """Main configuration for wrk-runner."""

    # Global settings
    duration: int = Field(default=30, description="Test duration in seconds")
    connections: int = Field(default=1000, description="Number of connections")
    threads: int = Field(default=8, description="Number of threads")
    warmup: int = Field(default=5, description="Warmup time in seconds")
    output_dir: str = Field(default="results", description="Output directory")
    lua_script: Optional[str] = Field(None, description="Lua script for wrk")

    # Visualization configuration
    generate_html_report: bool = Field(default=True, description="Generate HTML report")
    generate_json_export: bool = Field(default=True, description="Generate JSON export")
    chart_format: str = Field(
        default="html", description="Chart format: html, json, rich"
    )

    # Test definitions
    tests: List[TestConfig] = Field(..., description="List of tests to run")

    @validator("output_dir")
    def validate_output_dir(cls, v: str) -> str:
        Path(v).mkdir(parents=True, exist_ok=True)
        return v

    def get_test_config(self, test: TestConfig) -> Dict[str, Any]:
        """Get effective configuration for a test."""
        config = self.dict()

        # Override with test-specific values
        for field in ["duration", "connections", "threads", "warmup", "lua_script"]:
            test_value = getattr(test, field)
            if test_value is not None:
                config[field] = test_value

        return config
