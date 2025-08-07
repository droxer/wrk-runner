import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from wrk_runner.visualization.charts import ChartGenerator


class TestChartGenerator:
    """Tests for ChartGenerator class."""

    def test_initialization(self):
        """Test chart generator initialization."""
        generator = ChartGenerator()
        assert generator.results_dir.name == "results"

        generator = ChartGenerator("custom_results")
        assert generator.results_dir.name == "custom_results"

    def test_generate_rich_table(self):
        """Test rich table generation."""
        generator = ChartGenerator()

        results = [
            {
                "metadata": {"server": "test_api"},
                "performance": {
                    "requests_per_sec_summary": 1000.5,
                    "duration": "30s",
                    "transfer_per_sec": 1.2,
                    "transfer_unit": "MB",
                    "threads": 4,
                    "connections": 1000,
                },
                "latency": {"p50_ms": 10.5, "p99_ms": 50.2},
                "status_codes": {200: {"count": 5000, "percentage": 99.8}},
            }
        ]

        table = generator.generate_rich_table(results)
        assert table is not None
        assert table.title == "Performance Test Results"

    def test_generate_rich_table_empty(self):
        """Test rich table generation with empty results."""
        generator = ChartGenerator()
        results = []

        table = generator.generate_rich_table(results)
        assert table is not None
        assert table.title == "Performance Test Results"

    def test_generate_rich_table_missing_fields(self):
        """Test rich table generation with missing fields."""
        generator = ChartGenerator()

        results = [
            {
                "metadata": {"server": "test_api"},
                "performance": {},
                "latency": {},
                "status_codes": {},
            }
        ]

        table = generator.generate_rich_table(results)
        assert table is not None

    def test_generate_html_chart(self):
        """Test HTML chart generation."""
        generator = ChartGenerator()

        results = [
            {
                "metadata": {"server": "test_api"},
                "performance": {
                    "requests_per_sec_summary": 1000.5,
                    "duration": "30s",
                    "transfer_per_sec": 1.2,
                    "transfer_unit": "MB",
                    "threads": 4,
                    "connections": 1000,
                    "total_requests": 30000,
                },
                "latency": {"p50_ms": 10.5, "p99_ms": 50.2},
                "status_codes": {200: {"count": 5000, "percentage": 99.8}},
            }
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            generator.results_dir = Path(temp_dir)
            output_path = generator.generate_html_chart(results)

            assert Path(output_path).exists()
            assert output_path.endswith("performance_report.html")

            # Check HTML content
            content = Path(output_path).read_text()
            assert "WRK Performance Report" in content
            assert "test_api" in content
            assert "1000.5" in content or "1000.50" in content or "1,000.50" in content
            assert "10.5" in content or "10.50" in content
            assert "50.2" in content or "50.20" in content
            assert "1.2MB" in content or "1.2 MB" in content
            assert "chart.js" in content.lower()
            assert "bootstrap" in content

    def test_generate_html_chart_custom_filename(self):
        """Test HTML chart generation with custom filename."""
        generator = ChartGenerator()

        results = [
            {
                "metadata": {"server": "test_api"},
                "performance": {"requests_per_sec_summary": 1000.5},
                "latency": {"p50_ms": 10.5},
            }
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            generator.results_dir = Path(temp_dir)
            output_path = generator.generate_html_chart(results, "custom_report.html")

            assert Path(output_path).exists()
            assert output_path.endswith("custom_report.html")

    def test_generate_json_data(self):
        """Test JSON data generation for visualization."""
        generator = ChartGenerator()

        results = [
            {
                "metadata": {"server": "test_api"},
                "performance": {
                    "requests_per_sec_summary": 1000.5,
                    "total_requests": 30000,
                },
                "latency": {"p50_ms": 10.5, "p99_ms": 50.2},
            },
            {
                "metadata": {"server": "health_check"},
                "performance": {
                    "requests_per_sec_summary": 500.25,
                    "total_requests": 15000,
                },
                "latency": {"p50_ms": 5.2, "p99_ms": 25.1},
            },
        ]

        data = generator.generate_json_data(results)

        assert data["summary"]["total_tests"] == 2
        assert data["summary"]["test_names"] == ["test_api", "health_check"]
        assert data["summary"]["total_requests"] == 45000
        assert data["summary"]["avg_requests_per_sec"] == 750.375

        assert data["charts"]["requests_per_sec"]["labels"] == [
            "test_api",
            "health_check",
        ]
        assert data["charts"]["requests_per_sec"]["values"] == [1000.5, 500.25]

        assert data["charts"]["latency_percentiles"]["labels"] == [
            "test_api",
            "health_check",
        ]
        assert data["charts"]["latency_percentiles"]["p50"] == [10.5, 5.2]
        assert data["charts"]["latency_percentiles"]["p99"] == [50.2, 25.1]

    def test_generate_json_data_empty(self):
        """Test JSON data generation with empty results."""
        generator = ChartGenerator()

        results = []
        data = generator.generate_json_data(results)

        assert data["summary"]["total_tests"] == 0
        assert data["summary"]["test_names"] == []
        assert data["summary"]["total_requests"] == 0
        assert data["summary"]["avg_requests_per_sec"] == 0

        assert data["charts"]["requests_per_sec"]["labels"] == []
        assert data["charts"]["requests_per_sec"]["values"] == []

    def test_generate_html_table_rows(self):
        """Test HTML table rows generation."""
        generator = ChartGenerator()

        results = [
            {
                "metadata": {"server": "test_api"},
                "performance": {
                    "duration": "30s",
                    "threads": 4,
                    "connections": 1000,
                    "requests_per_sec_summary": 1000.5,
                    "transfer_per_sec": 1.2,
                    "transfer_unit": "MB",
                },
                "latency": {"p50_ms": 10.5, "p99_ms": 50.2},
            }
        ]

        rows = generator._generate_html_table_rows(results)
        assert "test_api" in rows
        assert "30s" in rows
        assert "4" in rows
        assert "1000" in rows
        assert "1000.50" in rows or "1,000.50" in rows
        assert "10.50ms" in rows
        assert "50.20ms" in rows
        assert "1.2MB" in rows or "1.2 MB" in rows

    def test_create_rich_charts(self):
        """Test rich console-based charts."""
        generator = ChartGenerator()

        results = [
            {
                "metadata": {"server": "test_api"},
                "performance": {"requests_per_sec_summary": 1000.5},
                "latency": {"p50_ms": 10.5},
            },
            {
                "metadata": {"server": "health_check"},
                "performance": {"requests_per_sec_summary": 500.25},
                "latency": {"p50_ms": 5.2},
            },
        ]

        with patch.object(generator.console, "print") as mock_print:
            generator.create_rich_charts(results)

            mock_print.assert_called()
            # Check that the chart header was printed
            chart_header_call = next(
                call
                for call in mock_print.call_args_list
                if "Requests/sec Chart" in str(call)
            )
            assert chart_header_call is not None

    def test_create_rich_charts_empty(self):
        """Test rich charts with empty results."""
        generator = ChartGenerator()

        results = []

        with patch.object(generator.console, "print") as mock_print:
            generator.create_rich_charts(results)

            mock_print.assert_called_with("[yellow]No results to display[/yellow]")

    def test_scan_and_visualize_html(self):
        """Test scanning and visualizing with HTML format."""
        generator = ChartGenerator()

        mock_results = [
            {
                "metadata": {"server": "test_api"},
                "performance": {"requests_per_sec_summary": 1000.5},
                "latency": {"p50_ms": 10.5},
            }
        ]

        with patch.object(
            generator.parser, "scan_and_parse_all", return_value=mock_results
        ):
            with tempfile.TemporaryDirectory() as temp_dir:
                generator.results_dir = Path(temp_dir)
                output_path = generator.scan_and_visualize("html")

                assert output_path.endswith("performance_report.html")
                assert Path(output_path).exists()

    def test_scan_and_visualize_json(self):
        """Test scanning and visualizing with JSON format."""
        generator = ChartGenerator()

        mock_results = [
            {
                "metadata": {"server": "test_api"},
                "performance": {"requests_per_sec_summary": 1000.5},
                "latency": {"p50_ms": 10.5},
            }
        ]

        with patch.object(
            generator.parser, "scan_and_parse_all", return_value=mock_results
        ):
            with tempfile.TemporaryDirectory() as temp_dir:
                generator.results_dir = Path(temp_dir)
                output_path = generator.scan_and_visualize("json")

                assert output_path.endswith("performance_data.json")
                assert Path(output_path).exists()

                # Check JSON content
                with open(output_path) as f:
                    data = json.load(f)
                    assert data["summary"]["total_tests"] == 1

    def test_scan_and_visualize_rich(self):
        """Test scanning and visualizing with rich format."""
        generator = ChartGenerator()

        mock_results = [
            {
                "metadata": {"server": "test_api"},
                "performance": {"requests_per_sec_summary": 1000.5},
                "latency": {"p50_ms": 10.5},
            }
        ]

        with patch.object(
            generator.parser, "scan_and_parse_all", return_value=mock_results
        ):
            with patch.object(generator, "create_rich_charts") as mock_charts:
                output_path = generator.scan_and_visualize("rich")
                assert output_path == ""
                mock_charts.assert_called_once_with(mock_results)

    def test_scan_and_visualize_no_results(self):
        """Test scanning when no results are found."""
        generator = ChartGenerator()

        with patch.object(generator.parser, "scan_and_parse_all", return_value=[]):
            with patch.object(generator.console, "print") as mock_print:
                result = generator.scan_and_visualize("html")
                assert result == ""
                mock_print.assert_called_with("[red]No wrk results found[/red]")

    def test_scan_and_visualize_invalid_format(self):
        """Test scanning with invalid format."""
        generator = ChartGenerator()

        mock_results = [
            {
                "metadata": {"server": "test_api"},
                "performance": {"requests_per_sec_summary": 1000.5},
                "latency": {"p50_ms": 10.5},
            }
        ]

        with patch.object(
            generator.parser, "scan_and_parse_all", return_value=mock_results
        ):
            result = generator.scan_and_visualize("invalid_format")
            assert result == ""
