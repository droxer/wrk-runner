import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from wrk_runner.core.config import Config, TestConfig
from wrk_runner.core.models import ServerMetrics, TestResult
from wrk_runner.core.tester import PerformanceTester


class TestPerformanceTester:
    """Tests for PerformanceTester class."""

    def test_initialization(self):
        """Test tester initialization."""
        config = Config(tests=[TestConfig(name="test", url="http://localhost:8000")])
        tester = PerformanceTester(config)

        assert tester.config == config
        assert tester.output_dir.name == "results"

    def test_initialization_custom_output_dir(self):
        """Test tester initialization with custom output directory."""
        config = Config(
            output_dir="custom_results",
            tests=[TestConfig(name="test", url="http://localhost:8000")],
        )
        tester = PerformanceTester(config)

        assert tester.output_dir.name == "custom_results"

    def test_command_exists_success(self):
        """Test command existence check when command exists."""
        config = Config(tests=[TestConfig(name="test", url="http://localhost:8000")])
        tester = PerformanceTester(config)

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0)
            assert tester._command_exists("wrk") is True

    def test_command_exists_failure(self):
        """Test command existence check when command doesn't exist."""
        config = Config(tests=[TestConfig(name="test", url="http://localhost:8000")])
        tester = PerformanceTester(config)

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = Exception("Command not found")
            assert tester._command_exists("nonexistent") is False

    def test_check_dependencies_success(self):
        """Test dependency check when all required dependencies are available."""
        config = Config(tests=[TestConfig(name="test", url="http://localhost:8000")])
        tester = PerformanceTester(config)

        with patch.object(tester, "_command_exists") as mock_exists:
            mock_exists.return_value = True
            assert tester.check_dependencies() is True

    def test_check_dependencies_missing_required(self):
        """Test dependency check when required dependencies are missing."""
        config = Config(tests=[TestConfig(name="test", url="http://localhost:8000")])
        tester = PerformanceTester(config)

        with patch.object(tester, "_command_exists") as mock_exists:
            mock_exists.side_effect = lambda cmd: cmd != "wrk"
            assert tester.check_dependencies() is False

    def test_parse_wrk_output_basic(self):
        """Test basic wrk output parsing."""
        config = Config(tests=[TestConfig(name="test", url="http://localhost:8000")])
        tester = PerformanceTester(config)

        output = """
Running 30s test @ http://localhost:8000/api
  4 threads and 1000 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    10.5ms    2.1ms   50.2ms   85.00%
    Req/Sec     1.50k   200.5    2.00k    75.00%
  50000 requests in 30.00s, 50.00MB read
Requests/sec:   1666.67
Transfer/sec:     1.67MB
  Latency Distribution
     50%    10.5ms
     75%    15.2ms
     90%    25.8ms
     99%    55.1ms
"""

        metrics = tester.parse_wrk_output(output)
        assert isinstance(metrics, ServerMetrics)
        assert metrics.requests_per_sec == 1666.67
        assert metrics.transfer_per_sec == "1.67MB"
        assert metrics.total_requests == 50000
        assert metrics.latency_50 == "10.5ms"
        assert metrics.latency_75 == "15.2ms"
        assert metrics.latency_90 == "25.8ms"
        assert metrics.latency_99 == "55.1ms"
        assert output in metrics.raw_output

    def test_parse_wrk_output_partial(self):
        """Test parsing wrk output with missing metrics."""
        config = Config(tests=[TestConfig(name="test", url="http://localhost:8000")])
        tester = PerformanceTester(config)

        output = """
Running 30s test @ http://localhost:8000/api
  4 threads and 1000 connections
"""

        metrics = tester.parse_wrk_output(output)
        assert isinstance(metrics, ServerMetrics)
        assert metrics.requests_per_sec is None
        assert metrics.transfer_per_sec is None
        assert metrics.total_requests is None
        assert metrics.total_errors is None

    def test_parse_wrk_output_with_errors(self):
        """Test parsing wrk output with socket errors."""
        config = Config(tests=[TestConfig(name="test", url="http://localhost:8000")])
        tester = PerformanceTester(config)

        output = """
Running 30s test @ http://localhost:8000/api
  4 threads and 1000 connections
  50000 requests in 30.00s, 50.00MB read
  Socket errors: connect 5, read 2, write 1, timeout 0
Requests/sec:   1666.67
"""

        metrics = tester.parse_wrk_output(output)
        assert isinstance(metrics, ServerMetrics)
        assert metrics.total_errors == 5

    @patch("subprocess.run")
    def test_run_test_success(self, mock_run):
        """Test successful test execution."""
        config = Config(
            tests=[TestConfig(name="test_api", url="http://localhost:8000/api")]
        )
        tester = PerformanceTester(config)

        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = """
Running 30s test @ http://localhost:8000/api
  2 threads and 100 connections
  1000 requests in 30.00s, 1.00MB read
Requests/sec:   33.33
Transfer/sec:     34.13KB
"""
        mock_run.return_value = mock_result

        with tempfile.TemporaryDirectory() as temp_dir:
            tester.output_dir = Path(temp_dir)
            result = tester.run_test(config.tests[0])

            assert result is not None
            assert isinstance(result, TestResult)
            assert result.server == "test_api"
            assert result.url == "http://localhost:8000/api"
            assert result.duration == 30
            assert result.connections == 1000  # default from global config
            assert result.threads == 8  # default
            assert result.metrics.requests_per_sec == 33.33
            assert result.output_file is not None
            assert result.json_file is not None

            # Check files were created
            assert Path(result.output_file).exists()
            assert Path(result.json_file).exists()

            # Check JSON file content
            with open(result.json_file) as f:
                json_data = json.load(f)
                assert json_data["server"] == "test_api"
                assert json_data["url"] == "http://localhost:8000/api"

    @patch("subprocess.run")
    def test_run_test_failure(self, mock_run):
        """Test test execution failure."""
        config = Config(
            tests=[TestConfig(name="test_api", url="http://localhost:8000/api")]
        )
        tester = PerformanceTester(config)

        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "Connection failed"
        mock_run.return_value = mock_result

        with tempfile.TemporaryDirectory() as temp_dir:
            tester.output_dir = Path(temp_dir)
            result = tester.run_test(config.tests[0])
            assert result is None

    @patch("subprocess.run")
    def test_run_test_timeout(self, mock_run):
        """Test test execution timeout."""
        config = Config(
            tests=[TestConfig(name="test_api", url="http://localhost:8000/api")]
        )
        tester = PerformanceTester(config)

        mock_run.side_effect = Exception("Timeout")

        with tempfile.TemporaryDirectory() as temp_dir:
            tester.output_dir = Path(temp_dir)
            result = tester.run_test(config.tests[0])
            assert result is None

    def test_run_test_with_lua_script(self):
        """Test test execution with Lua script."""
        config = Config(
            lua_script="test.lua",
            tests=[TestConfig(name="test_api", url="http://localhost:8000/api")],
        )
        tester = PerformanceTester(config)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".lua", delete=False) as f:
            f.write("-- Test lua script")
            lua_path = f.name

        try:
            config.lua_script = lua_path
            tester.config = config

            with patch("subprocess.run") as mock_run:
                mock_result = Mock()
                mock_result.returncode = 0
                mock_result.stdout = "Requests/sec:   100.0"
                mock_run.return_value = mock_result

                with tempfile.TemporaryDirectory() as temp_dir:
                    tester.output_dir = Path(temp_dir)
                    result = tester.run_test(config.tests[0])

                    assert result is not None
                    # Check that Lua script path was used in command
                    mock_run.assert_called_once()
                    call_args = mock_run.call_args[0][0]
                    assert "-s" in call_args
                    assert lua_path in call_args

        finally:
            Path(lua_path).unlink()

    @patch("subprocess.run")
    def test_run_all_tests(self, mock_run):
        """Test running all configured tests."""
        config = Config(
            tests=[
                TestConfig(name="test1", url="http://localhost:8000/api1"),
                TestConfig(name="test2", url="http://localhost:8000/api2"),
            ]
        )
        tester = PerformanceTester(config)

        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = """
Running 30s test @ http://localhost:8000/api
  2 threads and 100 connections
  1000 requests in 30.00s, 1.00MB read
Requests/sec:   33.33
"""
        mock_run.return_value = mock_result

        with tempfile.TemporaryDirectory() as temp_dir:
            tester.output_dir = Path(temp_dir)
            results = tester.run_all_tests()

            assert len(results) == 2
            assert all(isinstance(r, TestResult) for r in results)
            assert results[0].server == "test1"
            assert results[1].server == "test2"

    @patch("subprocess.run")
    @patch.object(PerformanceTester, "_command_exists")
    def test_run_all_tests_with_failure(self, mock_command_exists, mock_run):
        """Test running all tests with some failures."""
        config = Config(
            tests=[
                TestConfig(name="test1", url="http://localhost:8000/api1"),
                TestConfig(name="test2", url="http://localhost:8000/api2"),
            ]
        )
        tester = PerformanceTester(config)

        mock_command_exists.return_value = True

        def mock_run_side_effect(*args, **kwargs):
            cmd_str = str(args[0]) if args else ""
            if "api1" in cmd_str:
                mock_result = Mock()
                mock_result.returncode = 0
                mock_result.stdout = """Running 30s test @ http://localhost:8000/api1
  8 threads and 1000 connections
  100 requests in 30.00s, 1.00MB read
Requests/sec:   100.0"""
                return mock_result
            else:
                mock_result = Mock()
                mock_result.returncode = 1
                mock_result.stderr = "Connection failed"
                return mock_result

        mock_run.side_effect = mock_run_side_effect

        with tempfile.TemporaryDirectory() as temp_dir:
            tester.output_dir = Path(temp_dir)
            results = tester.run_all_tests()

            assert len(results) == 1
            assert results[0].server == "test1"

    def test_generate_report(self):
        """Test report generation."""
        config = Config(tests=[TestConfig(name="test", url="http://localhost:8000")])
        tester = PerformanceTester(config)

        results = [
            TestResult(
                server="test_api",
                url="http://localhost:8000/api",
                timestamp="20240101_120000",
                duration=30,
                connections=100,
                threads=8,
                metrics=ServerMetrics(requests_per_sec=100.0, transfer_per_sec="1.2MB"),
            )
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            tester.output_dir = Path(temp_dir)
            report_path = tester.generate_report(results)

            assert Path(report_path).exists()
            assert report_path.endswith(".md")

            # Check report content
            content = Path(report_path).read_text()
            assert "# Performance Test Report" in content
            assert "test_api" in content
            assert "http://localhost:8000/api" in content
            assert "100.0" in content
            assert "1.2MB" in content

    def test_generate_report_empty_results(self):
        """Test report generation with empty results."""
        config = Config(tests=[TestConfig(name="test", url="http://localhost:8000")])
        tester = PerformanceTester(config)

        with tempfile.TemporaryDirectory() as temp_dir:
            tester.output_dir = Path(temp_dir)
            report_path = tester.generate_report([])

            assert Path(report_path).exists()
            content = Path(report_path).read_text()
            assert "# Performance Test Report" in content

    def test_get_test_config_override(self):
        """Test getting effective test configuration with overrides."""
        config = Config(
            duration=30,
            connections=1000,
            threads=8,
            tests=[
                TestConfig(
                    name="test",
                    url="http://localhost:8000",
                    duration=60,
                    connections=500,
                )
            ],
        )
        tester = PerformanceTester(config)

        test_config = config.tests[0]
        effective_config = tester.config.get_test_config(test_config)

        assert effective_config["duration"] == 60
        assert effective_config["connections"] == 500
        assert effective_config["threads"] == 8
