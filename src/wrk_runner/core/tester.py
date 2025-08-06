"""Main performance testing functionality."""

import logging
import os
import re
import signal
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn

from .config import Config, ServerConfig, TestConfig
from .models import ServerMetrics, TestResult


class PerformanceTester:
    """Generic performance testing class using wrk."""

    def __init__(self, config: Config):
        self.config = config
        self.console = Console()
        self.logger = self._setup_logging()
        self.processes: List[subprocess.Popen] = []
        self.output_dir = Path(config.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _setup_logging(self) -> logging.Logger:
        """Setup rich logging."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",
            datefmt="[%X]",
            handlers=[RichHandler(console=self.console, rich_tracebacks=True)],
        )
        return logging.getLogger(__name__)

    def _signal_handler(self, signum, frame):
        """Handle interrupt signals gracefully."""
        self.logger.info("Received interrupt signal, cleaning up...")
        self.cleanup()
        sys.exit(0)

    def check_dependencies(self) -> bool:
        """Check if required dependencies are available."""
        required = ["wrk"]
        optional = ["jq", "gnuplot"]

        missing_required = []
        for dep in required:
            if not self._command_exists(dep):
                missing_required.append(dep)

        if missing_required:
            self.logger.error(f"Missing required dependencies: {missing_required}")
            self.logger.error("Install wrk:")
            self.logger.error("  macOS: brew install wrk")
            self.logger.error("  Ubuntu: sudo apt-get install wrk")
            self.logger.error("  From source: https://github.com/wg/wrk")
            return False

        missing_optional = []
        for dep in optional:
            if not self._command_exists(dep):
                missing_optional.append(dep)

        if missing_optional:
            self.logger.warning(f"Missing optional dependencies: {missing_optional}")

        return True

    def _command_exists(self, command: str) -> bool:
        """Check if a command exists in the system."""
        try:
            subprocess.run(
                ["which", command],
                capture_output=True,
                check=True,
                text=True,
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def wait_for_server(self, host: str, port: int, max_attempts: int = 30) -> bool:
        """Wait for server to be ready."""
        url = f"http://{host}:{port}"
        self.logger.info(f"Waiting for server at {url}...")

        for _attempt in range(max_attempts):
            try:
                urllib.request.urlopen(url, timeout=1)
                self.logger.info("Server ready")
                return True
            except (urllib.error.URLError, ConnectionError):
                time.sleep(1)

        self.logger.error("Server failed to start")
        return False

    def start_server(self, server_config: ServerConfig) -> bool:
        """Start a server based on configuration."""
        if not server_config.command:
            self.logger.error("No command specified for server")
            return False

        self.logger.info(f"Starting server: {server_config.name}")

        try:
            env = os.environ.copy()
            if server_config.env:
                env.update(server_config.env)

            process = subprocess.Popen(
                server_config.command,
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            self.processes.append(process)

            # Wait for server to be ready
            if server_config.port and not self.wait_for_server(
                server_config.host, server_config.port
            ):
                self.cleanup()
                return False

            # Warmup period
            warmup = self.config.warmup
            if warmup > 0:
                self.logger.info(f"Warming up for {warmup}s...")
                time.sleep(warmup)

            return True

        except Exception as e:
            self.logger.error(f"Failed to start server: {e}")
            return False

    def cleanup(self):
        """Clean up all running processes."""
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        self.processes.clear()

    def parse_wrk_output(self, output: str) -> ServerMetrics:
        """Parse wrk output to extract metrics."""
        metrics = ServerMetrics()

        # Parse requests/sec
        match = re.search(r"Requests/sec:\s+([\d.]+)", output)
        if match:
            metrics.requests_per_sec = float(match.group(1))

        # Parse transfer/sec
        match = re.search(r"Transfer/sec:\s+([\d.]+[KMGT]?B)", output)
        if match:
            metrics.transfer_per_sec = match.group(1)

        # Parse total requests
        match = re.search(r"(\d+) requests in", output)
        if match:
            metrics.total_requests = int(match.group(1))

        # Parse total errors
        match = re.search(r"Socket errors: (\d+)", output)
        if match:
            metrics.total_errors = int(match.group(1))

        # Parse latency distribution
        latency_patterns = {
            "latency_50": r"\s+50%\s+([\d.]+[msu]+)",
            "latency_75": r"\s+75%\s+([\d.]+[msu]+)",
            "latency_90": r"\s+90%\s+([\d.]+[msu]+)",
            "latency_99": r"\s+99%\s+([\d.]+[msu]+)",
        }

        for key, pattern in latency_patterns.items():
            match = re.search(pattern, output)
            if match:
                setattr(metrics, key, match.group(1))

        metrics.raw_output = output
        return metrics

    def run_test(self, test_config: TestConfig) -> Optional[TestResult]:
        """Run a performance test."""
        config = self.config.get_test_config(test_config)
        name = test_config.name
        url = test_config.url

        self.logger.info(f"Running performance test for [bold]{name}[/bold]")
        self.logger.info(f"URL: {url}")

        # Build wrk command
        cmd = [
            "wrk",
            f"-t{config['threads']}",
            f"-c{config['connections']}",
            f"-d{config['duration']}s",
            "--latency",
            url,
        ]

        # Add Lua script if provided
        lua_script = config.get("lua_script")
        if lua_script:
            lua_path = Path(lua_script)
            if lua_path.exists():
                cmd.extend(["-s", str(lua_path)])
                self.logger.info(f"Using Lua script: {lua_path}")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Run the test
        try:
            self.logger.info("Starting wrk test...")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=config["duration"] + 60,
            )

            if result.returncode != 0:
                self.logger.error(f"wrk failed: {result.stderr}")
                return None

            # Save raw output
            output_file = self.output_dir / f"wrk_{name}_{timestamp}.txt"
            output_file.write_text(result.stdout)

            # Parse metrics
            metrics = self.parse_wrk_output(result.stdout)

            test_result = TestResult(
                server=name,
                url=url,
                timestamp=timestamp,
                duration=config["duration"],
                connections=config["connections"],
                threads=config["threads"],
                metrics=metrics,
                config=config,
                output_file=str(output_file),
            )

            # Save JSON results
            json_file = self.output_dir / f"wrk_{name}_{timestamp}.json"
            json_file.write_text(test_result.model_dump_json(indent=2))
            test_result.json_file = str(json_file)

            self.logger.info(f"Results saved to: {output_file}")
            return test_result

        except subprocess.TimeoutExpired:
            self.logger.error("Test timed out")
            return None
        except Exception as e:
            self.logger.error(f"Test failed: {e}")
            return None

    def run_all_tests(self) -> List[TestResult]:
        """Run all configured tests."""
        results = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            task = progress.add_task("Running tests...", total=len(self.config.tests))

            for test_config in self.config.tests:
                try:
                    # Start server if needed
                    if test_config.server:
                        if not self.start_server(test_config.server):
                            progress.update(task, advance=1)
                            continue

                    # Run test
                    result = self.run_test(test_config)
                    if result:
                        results.append(result)

                    # Stop server if started
                    if test_config.server:
                        self.cleanup()
                        time.sleep(2)  # Cooldown

                except Exception as e:
                    self.logger.error(f"Test {test_config.name} failed: {e}")

                progress.update(task, advance=1)

        return results

    def generate_report(self, results: List[TestResult]) -> str:
        """Generate a summary report."""
        report_file = (
            self.output_dir
            / f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        )

        with open(report_file, "w") as f:
            f.write("# Performance Test Report\n")
            f.write(f"*Generated on {datetime.now().isoformat()}*\n\n")

            f.write("## Test Configuration\n")
            f.write(f"- Duration: {self.config.duration}s\n")
            f.write(f"- Connections: {self.config.connections}\n")
            f.write(f"- Threads: {self.config.threads}\n")
            f.write(f"- Warmup: {self.config.warmup}s\n")
            f.write(f"- Output Directory: {self.config.output_dir}\n\n")

            f.write("## Results\n\n")

            for result in results:
                f.write(f"### {result.server}\n")
                f.write(f"**URL**: {result.url}\n\n")

                if result.metrics.requests_per_sec:
                    f.write(f"**Requests/sec**: {result.metrics.requests_per_sec}\n")
                if result.metrics.transfer_per_sec:
                    f.write(f"**Transfer/sec**: {result.metrics.transfer_per_sec}\n")

                f.write("```\n")

                # Read raw output
                if result.output_file and Path(result.output_file).exists():
                    f.write(Path(result.output_file).read_text())

                f.write("\n```\n\n")

        self.logger.info(f"Report generated: {report_file}")
        return str(report_file)


