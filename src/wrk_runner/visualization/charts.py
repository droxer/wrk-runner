"""
Visualization charts and graphs for wrk-runner performance results.

Provides various chart types for visualizing performance test results including:
- Latency distribution charts
- Throughput over time
- Performance comparison charts
- Interactive HTML reports
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.table import Table

from ..core.parser import WRKParser


class ChartGenerator:
    """Generate various charts and visualizations for performance data."""

    def __init__(self, results_dir: str = "results"):
        self.results_dir = Path(results_dir)
        self.parser = WRKParser(results_dir)
        self.console = Console()

    def generate_rich_table(self, results: List[Dict[str, Any]]) -> Table:
        """Generate a rich table for terminal display."""
        table = Table(title="Performance Test Results")
        table.add_column("Server", style="cyan", no_wrap=True)
        table.add_column("Duration", style="magenta")
        table.add_column("Requests/sec", style="green", justify="right")
        table.add_column("Avg Latency", style="yellow", justify="right")
        table.add_column("P99 Latency", style="red", justify="right")
        table.add_column("Transfer/sec", style="blue", justify="right")
        table.add_column("Status Codes", style="white")

        for result in results:
            meta = result["metadata"]
            perf = result["performance"]
            latency = result["latency"]

            # Format status codes summary
            status_codes = result.get("status_codes", {})
            status_summary = (
                ", ".join(
                    [
                        f"{code}: {data['count']} ({data['percentage']:.1f}%)"
                        for code, data in status_codes.items()
                    ]
                )
                if status_codes
                else "-"
            )

            table.add_row(
                meta.get("server", "Unknown"),
                perf.get("duration", "N/A"),
                f"{perf.get('requests_per_sec_summary', 'N/A'):,.2f}",
                f"{latency.get('p50_ms', 'N/A'):.2f}ms",
                f"{latency.get('p99_ms', 'N/A'):.2f}ms",
                f"{perf.get('transfer_per_sec', 'N/A')} {perf.get('transfer_unit', 'B')}",
                status_summary,
            )

        return table

    def generate_html_chart(
        self,
        results: List[Dict[str, Any]],
        output_file: str = "performance_report.html",
    ) -> str:
        """Generate interactive HTML chart with Chart.js."""

        # Prepare data for Chart.js
        servers = [r["metadata"]["server"] for r in results]
        requests_per_sec = [
            r["performance"].get("requests_per_sec_summary", 0) for r in results
        ]
        latencies = [r["latency"].get("p50_ms", 0) for r in results]
        p99_latencies = [r["latency"].get("p99_ms", 0) for r in results]

        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>WRK Performance Report</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body {{ background-color: #f8f9fa; }}
                .chart-container {{ position: relative; height: 400px; margin: 20px 0; }}
                .metrics-card {{ background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            </style>
        </head>
        <body>
            <div class="container-fluid py-4">
                <div class="row">
                    <div class="col-12">
                        <h1 class="text-center mb-4">WRK Performance Report</h1>
                        <p class="text-center text-muted">Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    </div>
                </div>

                <div class="row">
                    <div class="col-md-6">
                        <div class="card metrics-card">
                            <div class="card-header">
                                <h5>Requests per Second</h5>
                            </div>
                            <div class="card-body">
                                <div class="chart-container">
                                    <canvas id="requestsChart"></canvas>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="col-md-6">
                        <div class="card metrics-card">
                            <div class="card-header">
                                <h5>Latency Comparison</h5>
                            </div>
                            <div class="card-body">
                                <div class="chart-container">
                                    <canvas id="latencyChart"></canvas>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="row">
                    <div class="col-12">
                        <div class="card metrics-card">
                            <div class="card-header">
                                <h5>Detailed Performance Metrics</h5>
                            </div>
                            <div class="card-body">
                                <div class="table-responsive">
                                    <table class="table table-striped">
                                        <thead>
                                            <tr>
                                                <th>Server</th>
                                                <th>Duration</th>
                                                <th>Threads</th>
                                                <th>Connections</th>
                                                <th>Requests/sec</th>
                                                <th>Avg Latency</th>
                                                <th>P99 Latency</th>
                                                <th>Transfer/sec</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {self._generate_html_table_rows(results)}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <script>
                // Requests per Second Chart
                const requestsCtx = document.getElementById('requestsChart').getContext('2d');
                new Chart(requestsCtx, {{
                    type: 'bar',
                    data: {{
                        labels: {json.dumps(servers)},
                        datasets: [{{
                            label: 'Requests/sec',
                            data: {json.dumps(requests_per_sec)},
                            backgroundColor: 'rgba(54, 162, 235, 0.8)',
                            borderColor: 'rgba(54, 162, 235, 1)',
                            borderWidth: 1
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {{
                            y: {{
                                beginAtZero: true,
                                title: {{
                                    display: true,
                                    text: 'Requests/sec'
                                }}
                            }}
                        }}
                    }}
                }});

                // Latency Chart
                const latencyCtx = document.getElementById('latencyChart').getContext('2d');
                new Chart(latencyCtx, {{
                    type: 'line',
                    data: {{
                        labels: {json.dumps(servers)},
                        datasets: [
                            {{
                                label: 'Average Latency',
                                data: {json.dumps(latencies)},
                                borderColor: 'rgba(255, 99, 132, 1)',
                                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                                tension: 0.1
                            }},
                            {{
                                label: '99th Percentile',
                                data: {json.dumps(p99_latencies)},
                                borderColor: 'rgba(255, 159, 64, 1)',
                                backgroundColor: 'rgba(255, 159, 64, 0.2)',
                                tension: 0.1
                            }}
                        ]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {{
                            y: {{
                                beginAtZero: true,
                                title: {{
                                    display: true,
                                    text: 'Latency (ms)'
                                }}
                            }}
                        }}
                    }}
                }});
            </script>
        </body>
        </html>
        """

        output_path = self.results_dir / output_file
        with open(output_path, "w") as f:
            f.write(html_template)

        return str(output_path)

    def _generate_html_table_rows(self, results: List[Dict[str, Any]]) -> str:
        """Generate HTML table rows from results."""
        rows = ""
        for result in results:
            meta = result["metadata"]
            perf = result["performance"]
            latency = result["latency"]

            rows += f"""
            <tr>
                <td>{meta.get('server', 'Unknown')}</td>
                <td>{perf.get('duration', 'N/A')}</td>
                <td>{perf.get('threads', 'N/A')}</td>
                <td>{perf.get('connections', 'N/A')}</td>
                <td>{perf.get('requests_per_sec_summary', 'N/A'):,.2f}</td>
                <td>{latency.get('p50_ms', 'N/A'):.2f}ms</td>
                <td>{latency.get('p99_ms', 'N/A'):.2f}ms</td>
                <td>{perf.get('transfer_per_sec', 'N/A')} {perf.get('transfer_unit', 'B')}</td>
            </tr>
            """
        return rows

    def generate_json_data(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate JSON data structure for visualization."""
        return {
            "summary": {
                "total_tests": len(results),
                "test_names": [r["metadata"]["server"] for r in results],
                "total_requests": sum(
                    r["performance"].get("total_requests", 0) for r in results
                ),
                "avg_requests_per_sec": (
                    sum(
                        r["performance"].get("requests_per_sec_summary", 0)
                        for r in results
                    )
                    / len(results)
                    if results
                    else 0
                ),
            },
            "data": results,
            "charts": {
                "requests_per_sec": {
                    "labels": [r["metadata"]["server"] for r in results],
                    "values": [
                        r["performance"].get("requests_per_sec_summary", 0)
                        for r in results
                    ],
                },
                "latency_percentiles": {
                    "labels": [r["metadata"]["server"] for r in results],
                    "p50": [r["latency"].get("p50_ms", 0) for r in results],
                    "p99": [r["latency"].get("p99_ms", 0) for r in results],
                },
            },
        }

    def create_rich_charts(self, results: List[Dict[str, Any]]) -> None:
        """Create rich console-based charts using Unicode characters."""
        if not results:
            self.console.print("[yellow]No results to display[/yellow]")
            return

        # Simple bar chart for requests/sec
        max_value = max(
            r["performance"].get("requests_per_sec_summary", 0) for r in results
        )

        self.console.print("\n[bold cyan]Requests/sec Chart[/bold cyan]")
        for result in results:
            server = result["metadata"]["server"]
            value = result["performance"].get("requests_per_sec_summary", 0)

            if max_value > 0:
                bar_length = int((value / max_value) * 50)
                bar = "█" * bar_length
                self.console.print(f"{server:20} |{bar} {value:,.0f}")

    def scan_and_visualize(
        self, output_format: str = "html", output_file: Optional[str] = None
    ) -> str:
        """Scan results and generate visualization."""
        results = self.parser.scan_and_parse_all()

        if not results:
            self.console.print("[red]No wrk results found[/red]")
            return ""

        if output_format == "html":
            filename = output_file or "performance_report.html"
            return self.generate_html_chart(results, filename)
        elif output_format == "json":
            filename = output_file or "performance_data.json"
            data = self.generate_json_data(results)
            with open(self.results_dir / filename, "w") as f:
                json.dump(data, f, indent=2)
            return str(self.results_dir / filename)
        elif output_format == "rich":
            self.create_rich_charts(results)
            return ""

        return ""
