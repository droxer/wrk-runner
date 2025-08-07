import json
import tempfile
from pathlib import Path
from unittest.mock import Mock

from rich.console import Console

from wrk_runner.core.models import ServerMetrics, TestResult
from wrk_runner.utils.output import (
    create_summary_table,
    export_results_csv,
    export_results_json,
    print_results_summary,
)


class TestOutputUtilities:
    """Tests for output utility functions."""

    def test_create_summary_table(self):
        """Test summary table creation."""
        results = [
            TestResult(
                server="test_api",
                url="http://localhost:8000/api",
                timestamp="20240101_120000",
                duration=30,
                connections=100,
                threads=2,
                metrics=ServerMetrics(
                    requests_per_sec=100.5,
                    transfer_per_sec="1.2MB",
                    latency_50="10ms",
                    latency_99="50ms",
                ),
            ),
            TestResult(
                server="health_check",
                url="http://localhost:8000/health",
                timestamp="20240101_120100",
                duration=30,
                connections=50,
                threads=1,
                metrics=ServerMetrics(
                    requests_per_sec=200.0,
                    transfer_per_sec="500KB",
                    latency_50="5ms",
                    latency_99="25ms",
                ),
            ),
        ]

        table = create_summary_table(results)
        assert table is not None
        assert table is not None

    def test_create_summary_table_empty(self):
        """Test summary table creation with empty results."""
        results = []
        table = create_summary_table(results)
        assert table is not None
        assert table.title == "Performance Test Results"

    def test_create_summary_table_with_none_values(self):
        """Test summary table creation with None values."""
        results = [
            TestResult(
                server="test_api",
                url="http://localhost:8000/api",
                timestamp="20240101_120000",
                duration=30,
                connections=100,
                threads=2,
                metrics=ServerMetrics(),  # All None values
            )
        ]

        table = create_summary_table(results)
        assert table is not None
        assert table is not None

    def test_export_results_json(self):
        """Test JSON export functionality."""
        results = [
            TestResult(
                server="test_api",
                url="http://localhost:8000/api",
                timestamp="20240101_120000",
                duration=30,
                connections=100,
                threads=2,
                metrics=ServerMetrics(
                    requests_per_sec=100.5,
                    transfer_per_sec="1.2MB",
                ),
            )
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "results.json"
            export_results_json(results, output_file)

            assert output_file.exists()
            with open(output_file) as f:
                data = json.load(f)

            assert data["timestamp"] == "20240101_120000"
            assert data["summary"]["total_tests"] == 1
            assert data["summary"]["successful_tests"] == 1
            assert len(data["results"]) == 1
            assert data["results"][0]["server"] == "test_api"
            assert data["results"][0]["metrics"]["requests_per_sec"] == 100.5

    def test_export_results_json_empty(self):
        """Test JSON export with empty results."""
        results = []

        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "results.json"
            export_results_json(results, output_file)

            assert output_file.exists()
            with open(output_file) as f:
                data = json.load(f)

            assert data["timestamp"] is None
            assert data["summary"]["total_tests"] == 0
            assert data["summary"]["successful_tests"] == 0
            assert data["results"] == []

    def test_export_results_csv(self):
        """Test CSV export functionality."""
        results = [
            TestResult(
                server="test_api",
                url="http://localhost:8000/api",
                timestamp="20240101_120000",
                duration=30,
                connections=100,
                threads=2,
                metrics=ServerMetrics(
                    requests_per_sec=100.5,
                    transfer_per_sec="1.2MB",
                    latency_50="10ms",
                    latency_75="15ms",
                    latency_90="25ms",
                    latency_99="50ms",
                ),
            )
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "results.csv"
            export_results_csv(results, output_file)

            assert output_file.exists()
            content = output_file.read_text()

            assert "server" in content
            assert "test_api" in content
            assert "http://localhost:8000/api" in content
            assert "100.5" in content
            assert "1.2MB" in content
            assert "10ms" in content

    def test_export_results_csv_empty(self):
        """Test CSV export with empty results."""
        results = []

        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "results.csv"
            export_results_csv(results, output_file)

            # Should not create file for empty results
            assert not output_file.exists()

    def test_export_results_csv_with_none_values(self):
        """Test CSV export with None values in metrics."""
        results = [
            TestResult(
                server="test_api",
                url="http://localhost:8000/api",
                timestamp="20240101_120000",
                duration=30,
                connections=100,
                threads=2,
                metrics=ServerMetrics(),  # All None values
            )
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "results.csv"
            export_results_csv(results, output_file)

            assert output_file.exists()
            content = output_file.read_text()

            # Should handle None values gracefully
            assert "test_api" in content
            assert "http://localhost:8000/api" in content

    def test_print_results_summary(self):
        """Test printing results summary to console."""
        results = [
            TestResult(
                server="test_api",
                url="http://localhost:8000/api",
                timestamp="20240101_120000",
                duration=30,
                connections=100,
                threads=2,
                metrics=ServerMetrics(
                    requests_per_sec=100.5,
                    transfer_per_sec="1.2MB",
                ),
            ),
            TestResult(
                server="health_check",
                url="http://localhost:8000/health",
                timestamp="20240101_120100",
                duration=30,
                connections=50,
                threads=1,
                metrics=ServerMetrics(
                    requests_per_sec=200.0,
                    transfer_per_sec="500KB",
                ),
            ),
        ]

        console = Mock(spec=Console)
        print_results_summary(console, results)

        # Verify console methods were called
        assert console.print.called

    def test_print_results_summary_empty(self):
        """Test printing empty results summary."""
        results = []
        console = Mock(spec=Console)
        print_results_summary(console, results)

        console.print.assert_called_with("[red]No results to display[/red]")

    def test_print_results_summary_with_partial_success(self):
        """Test summary with some successful and some failed tests."""
        results = [
            TestResult(
                server="test1",
                url="http://localhost:8000/api1",
                timestamp="20240101_120000",
                duration=30,
                connections=100,
                threads=2,
                metrics=ServerMetrics(requests_per_sec=100.0),
            ),
            TestResult(
                server="test2",
                url="http://localhost:8000/api2",
                timestamp="20240101_120100",
                duration=30,
                connections=100,
                threads=2,
                metrics=ServerMetrics(),  # No requests_per_sec
            ),
        ]

        console = Mock(spec=Console)
        print_results_summary(console, results)

        # Should show average and success ratio
        console.print.assert_called()
        # Find the call with average requests/sec
        avg_call = next(
            call
            for call in console.print.call_args_list
            if "Average requests/sec" in str(call)
        )
        assert "100.00" in str(avg_call)
        assert "Successful tests: 1/2" in str(console.print.call_args_list[-1][0][0])
