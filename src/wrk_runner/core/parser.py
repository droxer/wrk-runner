"""
Comprehensive wrk output parser for performance test results.

Provides detailed parsing of wrk output files with metrics extraction,
statistical analysis, and data normalization.
"""

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


@dataclass
class LatencyPercentiles:
    """Latency percentiles data structure."""

    p50: Optional[float] = None
    p75: Optional[float] = None
    p90: Optional[float] = None
    p95: Optional[float] = None
    p99: Optional[float] = None
    p99_9: Optional[float] = None


@dataclass
class ThreadStats:
    """Thread statistics data structure."""

    avg: Optional[float] = None
    stdev: Optional[float] = None
    max: Optional[float] = None
    stdev_percentage: Optional[float] = None


@dataclass
class TransferStats:
    """Transfer statistics data structure."""

    rate: Optional[float] = None
    unit: Optional[str] = None


@dataclass
class RequestStats:
    """Request statistics data structure."""

    total: Optional[int] = None
    rate: Optional[float] = None
    read_bytes: Optional[int] = None


@dataclass
class SocketStats:
    """Socket errors and statistics."""

    connect_errors: Optional[int] = None
    read_errors: Optional[int] = None
    write_errors: Optional[int] = None
    timeout_errors: Optional[int] = None


class WRKParser:
    """Advanced parser for wrk output files with comprehensive metrics extraction."""

    def __init__(self, results_dir: str = "results"):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def parse_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Parse a single wrk output file comprehensively."""
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path) as f:
            content = f.read()

        return {
            "metadata": self._parse_metadata(file_path),
            "configuration": self._parse_configuration(content),
            "performance": self._parse_performance_metrics(content),
            "latency": self._parse_latency_metrics(content),
            "transfer": self._parse_transfer_metrics(content),
            "socket_stats": self._parse_socket_stats(content),
            "status_codes": self._parse_status_codes(content),
            "latency_distribution": self._parse_latency_distribution(content),
            "raw_output": content,
        }

    def _parse_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from filename and path."""
        filename = file_path.stem

        # Extract server name and timestamp
        server_match = re.match(r"wrk_(.+?)_(\d{8}_\d{6})", filename)
        server = server_match.group(1) if server_match else "unknown"
        timestamp = (
            server_match.group(2)
            if server_match
            else datetime.now().strftime("%Y%m%d_%H%M%S")
        )

        return {
            "server": server,
            "timestamp": timestamp,
            "file_path": str(file_path),
            "file_size": file_path.stat().st_size,
        }

    def _parse_configuration(self, content: str) -> Dict[str, Any]:
        """Parse test configuration from wrk output."""
        config: Dict[str, Any] = {}

        # Threads and connections
        threads_conn = re.search(
            r"(\d+)\s+threads\s+and\s+(\d+)\s+connections", content
        )
        if threads_conn:
            config["threads"] = int(threads_conn.group(1))
            config["connections"] = int(threads_conn.group(2))

        # Duration
        duration = re.search(r"for\s+(\d+\.?\d*)([smhd])", content)
        if duration:
            value, unit = duration.groups()
            config["duration"] = float(value)
            config["duration_unit"] = unit

        # URL
        url = re.search(r"test\s+@\s+(.+)", content)
        if url:
            config["url"] = url.group(1).strip()

        return config

    def _parse_performance_metrics(self, content: str) -> Dict[str, Any]:
        """Parse performance metrics from wrk output."""
        metrics: Dict[str, Any] = {}

        # Latency statistics
        latency_line = re.search(
            r"Latency\s+(\d+\.?\d*)(\w+)\s+(\d+\.?\d*)(\w+)\s+(\d+\.?\d*)(\w+)\s+(\d+\.?\d*)%",
            content,
        )
        if latency_line:
            groups = latency_line.groups()
            metrics["latency"] = {
                "avg": float(groups[0]),
                "avg_unit": groups[1],
                "stdev": float(groups[2]),
                "stdev_unit": groups[3],
                "max": float(groups[4]),
                "max_unit": groups[5],
                "stdev_percentage": float(groups[6]),
            }

        # Request statistics
        req_line = re.search(
            r"Req/Sec\s+(\d+\.?\d*)(\w+)\s+(\d+\.?\d*)(\w+)\s+(\d+\.?\d*)(\w+)\s+(\d+\.?\d*)%",
            content,
        )
        if req_line:
            groups = req_line.groups()
            metrics["requests"] = {
                "per_sec": float(groups[0]),
                "per_sec_unit": groups[1],
                "stdev": float(groups[2]),
                "stdev_unit": groups[3],
                "max": float(groups[4]),
                "max_unit": groups[5],
                "stdev_percentage": float(groups[6]),
            }

        # Total requests and read bytes
        total_line = re.search(
            r"(\d+\.?\d*\w*)\s+requests\s+in\s+(\d+\.?\d*\w*),\s+([\d.]+[KMG]?B)\s+read",
            content,
        )
        if total_line:
            metrics["total_requests"] = int(self._parse_value(total_line.group(1)))
            metrics["duration_parsed"] = total_line.group(2)
            metrics["bytes_read"] = int(self._parse_value(total_line.group(3)))

        # Requests/sec summary
        summary_req = re.search(r"Requests/sec:\s+(\d+\.?\d*)", content)
        if summary_req:
            metrics["requests_per_sec_summary"] = float(summary_req.group(1))

        # Transfer/sec summary
        summary_transfer = re.search(r"Transfer/sec:\s+([\d.]+)\s*([KMG]?B)", content)
        if summary_transfer:
            metrics["transfer_per_sec"] = float(summary_transfer.group(1))
            metrics["transfer_unit"] = summary_transfer.group(2)

        return metrics

    def _parse_latency_metrics(self, content: str) -> Dict[str, Any]:
        """Parse detailed latency metrics including percentiles."""
        latency = {}

        # Standard percentiles
        percentiles = {
            "p50_ms": r"\s+50%\s+(\d+\.?\d*)",
            "p75_ms": r"\s+75%\s+(\d+\.?\d*)",
            "p90_ms": r"\s+90%\s+(\d+\.?\d*)",
            "p95_ms": r"\s+95%\s+(\d+\.?\d*)",
            "p99_ms": r"\s+99%\s+(\d+\.?\d*)",
            "p99_9_ms": r"\s+99\.9%\s+(\d+\.?\d*)",
        }

        for key, pattern in percentiles.items():
            match = re.search(pattern, content)
            if match:
                latency[key] = float(match.group(1))

        return latency

    def _parse_transfer_metrics(self, content: str) -> Dict[str, Any]:
        """Parse transfer-related metrics."""
        transfer: Dict[str, Any] = {}

        # Transfer/sec
        transfer_match = re.search(r"Transfer/sec:\s+(\d+\.?\d*)\s*([KMGT]?B)", content)
        if transfer_match:
            transfer["rate"] = float(transfer_match.group(1))
            transfer["unit"] = transfer_match.group(2)

        return transfer

    def _parse_socket_stats(self, content: str) -> Dict[str, int]:
        """Parse socket error statistics."""
        socket_stats: Dict[str, int] = {}

        # Socket errors
        socket_errors = re.search(
            r"Socket errors:\s+(\d+) connect,\s+(\d+) read,\s+(\d+) write,\s+(\d+) timeout",
            content,
        )
        if socket_errors:
            socket_stats.update(
                {
                    "connect_errors": int(socket_errors.group(1)),
                    "read_errors": int(socket_errors.group(2)),
                    "write_errors": int(socket_errors.group(3)),
                    "timeout_errors": int(socket_errors.group(4)),
                }
            )

        return socket_stats

    def _parse_status_codes(self, content: str) -> Dict[int, Dict[str, Any]]:
        """Parse HTTP status code distribution."""
        status_codes = {}

        # Status codes
        status_pattern = r"(\d{3}):\s+(\d+)\s+\((\d+\.?\d*)%\)"
        for status, count, percentage in re.findall(status_pattern, content):
            status_codes[int(status)] = {
                "count": int(count),
                "percentage": float(percentage),
            }

        return status_codes

    def _parse_latency_distribution(self, content: str) -> Dict[str, Any]:
        """Parse latency distribution buckets."""
        distribution = {}

        # Latency buckets
        bucket_patterns = {
            "under_1ms": r"\u003c 1ms:\s+(\d+) \((\d+\.?\d*)%\)",
            "under_2ms": r"\u003c 2ms:\s+(\d+) \((\d+\.?\d*)%\)",
            "under_5ms": r"\u003c 5ms:\s+(\d+) \((\d+\.?\d*)%\)",
            "under_10ms": r"\u003c 10ms:\s+(\d+) \((\d+\.?\d*)%\)",
            "under_20ms": r"\u003c 20ms:\s+(\d+) \((\d+\.?\d*)%\)",
            "under_50ms": r"\u003c 50ms:\s+(\d+) \((\d+\.?\d*)%\)",
            "under_100ms": r"\u003c 100ms:\s+(\d+) \((\d+\.?\d*)%\)",
            "under_200ms": r"\u003c 200ms:\s+(\d+) \((\d+\.?\d*)%\)",
            "under_500ms": r"\u003c 500ms:\s+(\d+) \((\d+\.?\d*)%\)",
            "under_1000ms": r"\u003c 1000ms:\s+(\d+) \((\d+\.?\d*)%\)",
            "over_1000ms": r"\u003e 1000ms:\s+(\d+) \((\d+\.?\d*)%\)",
        }

        for key, pattern in bucket_patterns.items():
            match = re.search(pattern, content)
            if match:
                distribution[key] = {
                    "count": int(match.group(1)),
                    "percentage": float(match.group(2)),
                }

        return distribution

    def _parse_value(self, value_str: str) -> float:
        """Parse value with K/M/G suffix."""
        value_str = str(value_str).upper()
        multipliers = {
            "GB": 1000000000,
            "MB": 1000000,
            "KB": 1000,
            "G": 1000000000,
            "M": 1000000,
            "K": 1000,
        }

        # Sort by length (longest first) to avoid partial matches
        for suffix, multiplier in sorted(
            multipliers.items(), key=lambda x: len(x[0]), reverse=True
        ):
            if value_str.endswith(suffix):
                return float(value_str[: -len(suffix)]) * multiplier

        return float(value_str)

    def scan_and_parse_all(self) -> List[Dict[str, Any]]:
        """Scan directory and parse all wrk output files."""
        results = []
        pattern = "wrk_*.txt"

        for file_path in self.results_dir.glob(pattern):
            try:
                result = self.parse_file(file_path)
                results.append(result)
            except Exception as e:
                print(f"Error parsing {file_path}: {e}")

        return results

    def get_summary_stats(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics from parsed results."""
        if not results:
            return {}

        summary = {
            "total_tests": len(results),
            "test_names": [r["metadata"]["server"] for r in results],
            "total_requests": sum(
                r["performance"].get("total_requests", 0) for r in results
            ),
            "avg_requests_per_sec": 0,
            "avg_latency": 0,
            "tests": results,
        }

        # Calculate averages
        valid_results = [
            r for r in results if r["performance"].get("requests_per_sec_summary")
        ]
        if valid_results:
            summary["avg_requests_per_sec"] = sum(
                r["performance"]["requests_per_sec_summary"] for r in valid_results
            ) / len(valid_results)

        valid_latency = [r for r in results if r["latency"].get("p50_ms")]
        if valid_latency:
            summary["avg_latency"] = sum(
                r["latency"]["p50_ms"] for r in valid_latency
            ) / len(valid_latency)

        return summary
