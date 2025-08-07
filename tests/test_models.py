from datetime import datetime

from wrk_runner.core.models import ServerMetrics, TestResult


class TestServerMetrics:
    """Tests for ServerMetrics model."""

    def test_server_metrics_basic(self):
        """Test basic ServerMetrics creation."""
        metrics = ServerMetrics(
            requests_per_sec=1000.5,
            transfer_per_sec="1.2MB",
            latency_50="10ms",
            latency_75="20ms",
            latency_90="50ms",
            latency_99="100ms",
            total_requests=50000,
            total_errors=5,
        )

        assert metrics.requests_per_sec == 1000.5
        assert metrics.transfer_per_sec == "1.2MB"
        assert metrics.latency_50 == "10ms"
        assert metrics.latency_75 == "20ms"
        assert metrics.latency_90 == "50ms"
        assert metrics.latency_99 == "100ms"
        assert metrics.total_requests == 50000
        assert metrics.total_errors == 5

    def test_server_metrics_defaults(self):
        """Test ServerMetrics with default values."""
        metrics = ServerMetrics()

        assert metrics.requests_per_sec is None
        assert metrics.transfer_per_sec is None
        assert metrics.latency_50 is None
        assert metrics.latency_75 is None
        assert metrics.latency_90 is None
        assert metrics.latency_99 is None
        assert metrics.total_requests is None
        assert metrics.total_errors is None
        assert metrics.raw_output is None

    def test_server_metrics_with_raw_output(self):
        """Test ServerMetrics with raw output."""
        raw_output = (
            "Running 30s test @ http://localhost:8000\n  2 threads and 100 connections"
        )
        metrics = ServerMetrics(raw_output=raw_output)

        assert metrics.raw_output == raw_output

    def test_server_metrics_extra_fields(self):
        """Test ServerMetrics allows extra fields."""
        metrics = ServerMetrics(
            requests_per_sec=1000.0,
            custom_field="custom_value",
            another_field=123,
        )

        assert metrics.requests_per_sec == 1000.0
        assert metrics.custom_field == "custom_value"  # type: ignore
        assert metrics.another_field == 123  # type: ignore

    def test_server_metrics_serialization(self):
        """Test ServerMetrics JSON serialization."""
        metrics = ServerMetrics(
            requests_per_sec=1000.5,
            transfer_per_sec="1.2MB",
            total_requests=50000,
        )

        json_str = metrics.model_dump_json()
        deserialized = ServerMetrics.model_validate_json(json_str)

        assert deserialized.requests_per_sec == 1000.5
        assert deserialized.transfer_per_sec == "1.2MB"
        assert deserialized.total_requests == 50000


class TestTestResult:
    """Tests for TestResult model."""

    def test_test_result_basic(self):
        """Test basic TestResult creation."""
        result = TestResult(
            server="test_server",
            url="http://localhost:8000/api",
            duration=30,
            connections=100,
            threads=2,
        )

        assert result.server == "test_server"
        assert result.url == "http://localhost:8000/api"
        assert result.duration == 30
        assert result.connections == 100
        assert result.threads == 2
        assert isinstance(result.timestamp, str)
        assert result.metrics == ServerMetrics()
        assert result.config == {}
        assert result.output_file is None
        assert result.json_file is None

    def test_test_result_with_metrics(self):
        """Test TestResult with custom metrics."""
        metrics = ServerMetrics(requests_per_sec=1500.0, total_requests=45000)
        result = TestResult(
            server="test_server",
            url="http://localhost:8000/api",
            duration=30,
            connections=100,
            threads=2,
            metrics=metrics,
        )

        assert result.metrics.requests_per_sec == 1500.0
        assert result.metrics.total_requests == 45000

    def test_test_result_with_files(self):
        """Test TestResult with file paths."""
        result = TestResult(
            server="test_server",
            url="http://localhost:8000/api",
            duration=30,
            connections=100,
            threads=2,
            output_file="results/test_output.txt",
            json_file="results/test_output.json",
        )

        assert result.output_file == "results/test_output.txt"
        assert result.json_file == "results/test_output.json"

    def test_test_result_with_config(self):
        """Test TestResult with configuration."""
        config = {"lua_script": "test.lua", "warmup": 5}
        result = TestResult(
            server="test_server",
            url="http://localhost:8000/api",
            duration=30,
            connections=100,
            threads=2,
            config=config,
        )

        assert result.config == config

    def test_test_result_timestamp_generation(self):
        """Test timestamp is auto-generated."""
        before = datetime.now().isoformat()
        result = TestResult(
            server="test_server",
            url="http://localhost:8000/api",
            duration=30,
            connections=100,
            threads=2,
        )
        after = datetime.now().isoformat()

        assert before <= result.timestamp <= after

    def test_test_result_extra_fields(self):
        """Test TestResult allows extra fields."""
        result = TestResult(
            server="test_server",
            url="http://localhost:8000/api",
            duration=30,
            connections=100,
            threads=2,
            custom_data={"key": "value"},
        )

        assert result.custom_data == {"key": "value"}  # type: ignore

    def test_test_result_serialization(self):
        """Test TestResult JSON serialization."""
        metrics = ServerMetrics(requests_per_sec=2000.0)
        config = {"test": "config"}
        result = TestResult(
            server="test_server",
            url="http://localhost:8000/api",
            duration=30,
            connections=100,
            threads=2,
            metrics=metrics,
            config=config,
        )

        json_str = result.model_dump_json()
        deserialized = TestResult.model_validate_json(json_str)

        assert deserialized.server == "test_server"
        assert deserialized.url == "http://localhost:8000/api"
        assert deserialized.duration == 30
        assert deserialized.connections == 100
        assert deserialized.threads == 2
        assert deserialized.metrics.requests_per_sec == 2000.0
        assert deserialized.config == config

    def test_test_result_dict_conversion(self):
        """Test TestResult to dict conversion."""
        result = TestResult(
            server="test_server",
            url="http://localhost:8000/api",
            duration=30,
            connections=100,
            threads=2,
        )

        result_dict = result.model_dump()

        assert result_dict["server"] == "test_server"
        assert result_dict["url"] == "http://localhost:8000/api"
        assert result_dict["duration"] == 30
        assert result_dict["connections"] == 100
        assert result_dict["threads"] == 2
        assert "timestamp" in result_dict
        assert "metrics" in result_dict
