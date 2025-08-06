"""Output utilities for wrk-reporter."""

import json
from pathlib import Path
from typing import List

from rich.console import Console
from rich.table import Table

from ..core.models import TestResult


def create_summary_table(results: List[TestResult]) -> Table:
    """Create a rich table with test results summary."""
    table = Table(title="Performance Test Results")
    table.add_column("Server", style="cyan", no_wrap=True)
    table.add_column("URL", style="magenta")
    table.add_column("Requests/sec", style="green", justify="right")
    table.add_column("Transfer/sec", style="blue", justify="right")
    table.add_column("Latency 50%", style="yellow", justify="right")
    table.add_column("Latency 99%", style="red", justify="right")

    for result in results:
        table.add_row(
            result.server,
            result.url,
            str(result.metrics.requests_per_sec or "N/A"),
            str(result.metrics.transfer_per_sec or "N/A"),
            str(result.metrics.latency_50 or "N/A"),
            str(result.metrics.latency_99 or "N/A"),
        )

    return table


def export_results_json(results: List[TestResult], output_file: Path) -> None:
    """Export test results to JSON format."""
    data = {
        "timestamp": results[0].timestamp if results else None,
        "summary": {
            "total_tests": len(results),
            "successful_tests": len([r for r in results if r.metrics.requests_per_sec]),
        },
        "results": [result.model_dump() for result in results],
    }

    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)


def export_results_csv(results: List[TestResult], output_file: Path) -> None:
    """Export test results to CSV format."""
    import csv

    if not results:
        return

    fieldnames = [
        "server",
        "url",
        "timestamp",
        "duration",
        "connections",
        "threads",
        "requests_per_sec",
        "transfer_per_sec",
        "latency_50",
        "latency_75",
        "latency_90",
        "latency_99",
    ]

    with open(output_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for result in results:
            row = {
                "server": result.server,
                "url": result.url,
                "timestamp": result.timestamp,
                "duration": result.duration,
                "connections": result.connections,
                "threads": result.threads,
                "requests_per_sec": result.metrics.requests_per_sec,
                "transfer_per_sec": result.metrics.transfer_per_sec,
                "latency_50": result.metrics.latency_50,
                "latency_75": result.metrics.latency_75,
                "latency_90": result.metrics.latency_90,
                "latency_99": result.metrics.latency_99,
            }
            writer.writerow(row)


def print_results_summary(console: Console, results: List[TestResult]) -> None:
    """Print a summary of test results to console."""
    if not results:
        console.print("[red]No results to display[/red]")
        return

    console.print(create_summary_table(results))

    # Summary statistics
    successful = [r for r in results if r.metrics.requests_per_sec]
    if successful:
        avg_rps = (
            sum(
                r.metrics.requests_per_sec
                for r in successful
                if r.metrics.requests_per_sec is not None
            )
            / len(successful)
            if successful
            else 0.0
        )
        console.print(f"\n[green]Average requests/sec: {avg_rps:.2f}[/green]")
        console.print(
            f"[blue]Successful tests: {len(successful)}/{len(results)}[/blue]"
        )
