"""Main CLI entry point for wrk-reporter."""

import json
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table

try:
    import yaml  # type: ignore[import-untyped]
except ImportError:
    yaml = None

from ..core.config import Config, TestConfig
from ..core.parser import WRKParser
from ..core.tester import PerformanceTester
from ..visualization.charts import ChartGenerator

console = Console()


@click.group()
@click.version_option()
def cli() -> None:
    """Generic performance testing framework using wrk."""
    pass


@cli.command()
@click.argument("url", required=False)
@click.option(
    "-c",
    "--config",
    default="performance_config.json",
    help="Configuration file (JSON or YAML)",
)
@click.option("-d", "--duration", type=int, help="Test duration in seconds")
@click.option("--connections", type=int, help="Number of connections")
@click.option("--threads", type=int, help="Number of threads")
@click.option("-w", "--warmup", type=int, help="Warmup time in seconds")
@click.option("-o", "--output", help="Output directory")
@click.option("-s", "--lua-script", help="Lua script for wrk")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.option("--name", help="Test name for quick mode")
def test(
    url: Optional[str],
    config: str,
    duration: Optional[int],
    connections: Optional[int],
    threads: Optional[int],
    warmup: Optional[int],
    output: Optional[str],
    lua_script: Optional[str],
    verbose: bool,
    name: Optional[str],
) -> None:
    """Run performance tests from configuration file or quick test with URL."""
    if verbose:
        import logging

        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # Quick test mode - use URL argument
        if url:
            config_obj = Config(
                duration=duration or 30,
                connections=connections or 100,
                threads=threads or 2,
                warmup=warmup or 5,
                output_dir=output or "quick_test",
                lua_script=lua_script,
                tests=[TestConfig(name=name or "quick_test", url=url)],
            )
        else:
            # Configuration file mode
            config_path = Path(config)
            if not config_path.exists():
                console.print(f"[red]Configuration file not found: {config}[/red]")
                sys.exit(1)

            if config_path.suffix.lower() in [".yml", ".yaml"]:
                import yaml

                with open(config_path) as f:
                    config_data = yaml.safe_load(f)
            else:
                with open(config_path) as f:
                    config_data = json.load(f)

            # Create config object
            config_obj = Config(**config_data)

            # Override with CLI arguments
            if duration:
                config_obj.duration = duration
            if connections:
                config_obj.connections = connections
            if threads:
                config_obj.threads = threads
            if warmup is not None:
                config_obj.warmup = warmup
            if output:
                config_obj.output_dir = output
            if lua_script:
                config_obj.lua_script = lua_script

        # Run tests
        tester = PerformanceTester(config_obj)
        if not tester.check_dependencies():
            sys.exit(1)

        results = tester.run_all_tests()

        if results:
            report_file = tester.generate_report(results)

            if url:
                # Quick test mode output
                console.print("\n[green]✓ Quick test complete![/green]")
                for result in results:
                    console.print(f"[blue]URL:[/blue] {result.url}")
                    console.print(
                        f"[green]Requests/sec:[/green] {result.metrics.requests_per_sec}"
                    )
                    console.print(
                        f"[blue]Transfer/sec:[/blue] {result.metrics.transfer_per_sec}"
                    )
            else:
                # Configuration file mode output
                console.print("\n[green]✓ Performance testing complete![/green]")
                console.print(f"[blue]📊 Report: {report_file}[/blue]")

                # Display summary table
                table = Table(title="Test Results Summary")
                table.add_column("Server", style="cyan")
                table.add_column("URL", style="magenta")
                table.add_column("Requests/sec", style="green")
                table.add_column("Transfer/sec", style="blue")

                for result in results:
                    table.add_row(
                        result.server,
                        result.url,
                        str(result.metrics.requests_per_sec or "N/A"),
                        str(result.metrics.transfer_per_sec or "N/A"),
                    )

                console.print(table)
        else:
            console.print("[red]✗ No tests completed successfully[/red]")
            sys.exit(1)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option(
    "-f",
    "--format",
    type=click.Choice(["json", "yaml"]),
    default="json",
    help="Config format",
)
@click.option("--output", "-o", default="performance_config.json", help="Output file")
def init_config(format: str, output: str) -> None:
    """Create sample configuration file."""
    sample_config = {
        "duration": 30,
        "connections": 1000,
        "threads": 8,
        "warmup": 5,
        "output_dir": "results",
        "tests": [
            {
                "name": "example_api",
                "url": "http://localhost:8080/api",
            },
            {
                "name": "external_service",
                "url": "http://httpbin.org/get",
            },
        ],
    }

    output_path = Path(output)

    if format == "yaml":
        import yaml

        output_path = output_path.with_suffix(".yaml")
        with open(output_path, "w") as f:
            yaml.dump(sample_config, f, default_flow_style=False)
    else:
        with open(output_path, "w") as f:
            json.dump(sample_config, f, indent=2)

    console.print(f"[green]✓ Sample configuration created: {output_path}[/green]")


@cli.command()
@click.argument("config_file")
def validate(config_file: str) -> None:
    """Validate configuration file."""
    try:
        config_path = Path(config_file)
        if not config_path.exists():
            console.print(f"[red]Configuration file not found: {config_file}[/red]")
            sys.exit(1)

        if config_path.suffix.lower() in [".yml", ".yaml"]:
            import yaml

            with open(config_path) as f:
                config_data = yaml.safe_load(f)
        else:
            with open(config_path) as f:
                config_data = json.load(f)

        # Validate with Pydantic
        config = Config(**config_data)

        console.print("[green]✓ Configuration is valid[/green]")
        console.print(f"[blue]Tests configured: {len(config.tests)}[/blue]")

        for test in config.tests:
            console.print(f"[green]✓[/green] {test.name} → {test.url}")

    except Exception as e:
        console.print(f"[red]Validation failed: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument("file_path", required=False)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "yaml", "table"]),
    default="table",
    help="Output format",
)
@click.option("--output", "-o", help="Output file for parsed data")
def parse(file_path: Optional[str], format: str, output: Optional[str]) -> None:
    """Parse wrk output file(s) and display results."""
    parser = WRKParser()

    if file_path:
        # Parse single file
        try:
            result = parser.parse_file(file_path)
            results = [result]
        except Exception as e:
            console.print(f"[red]Error parsing file: {e}[/red]")
            sys.exit(1)
    else:
        # Scan and parse all files in results directory
        results = parser.scan_and_parse_all()
        if not results:
            console.print(
                "[yellow]No wrk output files found in results directory[/yellow]"
            )
            return

    if format == "json":
        output_data = parser.get_summary_stats(results)
        if output:
            with open(output, "w") as f:
                json.dump(output_data, f, indent=2)
            console.print(f"[green]✓ Parsed data saved to {output}[/green]")
        else:
            console.print(json.dumps(output_data, indent=2))

    elif format == "yaml":
        import yaml

        output_data = parser.get_summary_stats(results)
        if output:
            with open(output, "w") as f:
                yaml.dump(output_data, f, default_flow_style=False)
            console.print(f"[green]✓ Parsed data saved to {output}[/green]")
        else:
            yaml.dump(output_data, sys.stdout, default_flow_style=False)

    else:  # table format
        table = Table(title="WRK Performance Results")
        table.add_column("Server", style="cyan")
        table.add_column("Duration", style="magenta")
        table.add_column("Requests/sec", style="green", justify="right")
        table.add_column("Avg Latency", style="yellow", justify="right")
        table.add_column("P99 Latency", style="red", justify="right")
        table.add_column("Transfer/sec", style="blue", justify="right")

        for result in results:
            meta = result["metadata"]
            perf = result["performance"]
            latency = result["latency"]

            table.add_row(
                meta.get("server", "Unknown"),
                perf.get("duration_parsed", "N/A"),
                f"{perf.get('requests_per_sec_summary', 'N/A'):,.2f}",
                f"{latency.get('p50_ms', 'N/A'):.2f}ms",
                f"{latency.get('p99_ms', 'N/A'):.2f}ms",
                f"{perf.get('transfer_per_sec', 'N/A')} {perf.get('transfer_unit', 'B')}",
            )

        console.print(table)


@cli.command()
@click.option(
    "--format",
    "-f",
    type=click.Choice(["html", "json", "rich"]),
    default="html",
    help="Output format",
)
@click.option("--output", "-o", help="Output file name")
@click.option(
    "--results-dir", "-r", default="results", help="Results directory to scan"
)
@click.option("--open", is_flag=True, help="Open HTML report in browser")
def visualize(format: str, output: Optional[str], results_dir: str, open: bool) -> None:
    """Generate visualizations from wrk output files."""
    try:
        generator = ChartGenerator(results_dir)

        if format == "html":
            report_path = generator.scan_and_visualize("html", output)
            if report_path:
                console.print(f"[green]✓ HTML report generated: {report_path}[/green]")
                if open:
                    import webbrowser

                    webbrowser.open(f"file://{Path(report_path).absolute()}")
                    console.print("[blue]📊 Opening report in browser...[/blue]")

        elif format == "json":
            data_path = generator.scan_and_visualize("json", output)
            if data_path:
                console.print(f"[green]✓ JSON data exported: {data_path}[/green]")

        elif format == "rich":
            generator.scan_and_visualize("rich")

    except Exception as e:
        console.print(f"[red]Error generating visualization: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    cli()
