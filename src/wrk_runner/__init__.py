"""
wrk-runner: Generic performance testing framework using wrk.

A modern, configurable performance testing tool built on top of wrk for
load testing HTTP servers and APIs.
"""

__version__ = "0.1.0"
__author__ = "Performance Testing Team"
__email__ = "team@example.com"

from .core.config import Config, ServerConfig, TestConfig
from .core.models import ServerMetrics, TestResult
from .core.parser import WRKParser
from .core.tester import PerformanceTester
from .visualization.charts import ChartGenerator

__all__ = [
    "PerformanceTester",
    "Config",
    "TestConfig",
    "ServerConfig",
    "TestResult",
    "ServerMetrics",
    "WRKParser",
    "ChartGenerator",
]
