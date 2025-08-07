import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.table import Table

from ..core.parser import WRKParser


class ChartGenerator:
    def __init__(self, results_dir: str = "results"):
        self.results_dir = Path(results_dir)
        self.parser = WRKParser(results_dir)
        self.console = Console()

    def generate_rich_table(self, results: List[Dict[str, Any]]) -> Table:
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
                f"{float(perf.get('requests_per_sec_summary', 0)):.2f}",
                f"{float(latency.get('p50_ms', 0)):.2f}ms",
                f"{float(latency.get('p99_ms', 0)):.2f}ms",
                f"{perf.get('transfer_per_sec', 'N/A')} {perf.get('transfer_unit', 'B')}",
                status_summary,
            )
        return table

    def generate_html_chart(
        self,
        results: List[Dict[str, Any]],
        output_file: str = "performance_report.html",
    ) -> str:
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
    <title>Performance Test Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .chart-container {{ width: 100%; max-width: 800px; margin: 20px 0; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <h1>Performance Test Report</h1>
    <div class="chart-container">
        <canvas id="requestsChart"></canvas>
    </div>
    <div class="chart-container">
        <canvas id="latencyChart"></canvas>
    </div>
    <table>
        <thead>
            <tr>
                <th>Server</th>
                <th>Requests/sec</th>
                <th>Avg Latency (ms)</th>
                <th>P99 Latency (ms)</th>
            </tr>
        </thead>
        <tbody>
            {self._generate_html_table_rows(results)}
        </tbody>
    </table>
    <script>
        const ctx1 = document.getElementById('requestsChart').getContext('2d');
        new Chart(ctx1, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(servers)},
                datasets: [{{
                    label: 'Requests/sec',
                    data: {json.dumps(requests_per_sec)},
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false
            }}
        }});

        const ctx2 = document.getElementById('latencyChart').getContext('2d');
        new Chart(ctx2, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(servers)},
                datasets: [
                    {{
                        label: 'Avg Latency (ms)',
                        data: {json.dumps(latencies)},
                        backgroundColor: 'rgba(255, 99, 132, 0.2)',
                        borderColor: 'rgba(255, 99, 132, 1)',
                        borderWidth: 1
                    }},
                    {{
                        label: 'P99 Latency (ms)',
                        data: {json.dumps(p99_latencies)},
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false
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
        rows = ""
        for result in results:
            meta = result["metadata"]
            perf = result["performance"]
            latency = result["latency"]
            rows += f"""
            <tr>
                <td>{meta.get('server', 'Unknown')}</td>
                <td>{float(perf.get('requests_per_sec_summary', 0)):.2f}</td>
                <td>{float(latency.get('p50_ms', 0)):.2f}</td>
                <td>{float(latency.get('p99_ms', 0)):.2f}</td>
            </tr>
            """
        return rows

    def generate_json_data(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
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
        if not results:
            self.console.print("[yellow]No results to display[/yellow]")
            return
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
