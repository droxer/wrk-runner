# wrk-runner

Generic performance testing framework using wrk for load testing HTTP servers and APIs.

## Features

- 🚀 **Easy to use**: Simple CLI and JSON/YAML configuration
- 🔧 **Generic**: Works with any HTTP server or API
- 📊 **Rich output**: Beautiful tables and detailed reports
- 🔌 **Extensible**: Plugin architecture for custom reporters
- 🎯 **Precise**: Accurate metrics with latency distribution
- 📈 **Multiple formats**: JSON, CSV, Markdown reports

## Installation

### Using pip

```bash
pip install wrk-runner
```

### Using uv

```bash
uv tool install wrk-runner
```

### From source

```bash
git clone https://github.com/droxer/wrk-runner
cd wrk-runner
uv pip install -e .
```

## Quick Start

### Quick Test

```bash
# Test any URL
wrk-runner https://httpbin.org/get

# With custom parameters
wrk-runner https://api.example.com -d 60 -c 1000 -t 8
```

### Configuration-based Testing

```bash
# Create sample configuration
wrk-runner --create-sample

# Run tests from configuration
wrk-runner
```

## Configuration

### Basic Configuration (JSON)

```json
{
  "duration": 30,
  "connections": 1000,
  "threads": 8,
  "warmup": 5,
  "output_dir": "results",
  "tests": [
    {
      "name": "my_api",
      "url": "http://localhost:3000/api/v1/users",
      "server": {
        "name": "nodejs_api",
        "command": ["npm", "start"],
        "port": 3000
      }
    }
  ]
}
```

### YAML Configuration

```yaml
duration: 30
connections: 1000
threads: 8
warmup: 5
output_dir: results
tests:
  - name: fasthttp
    url: http://localhost:8081
    server:
      name: fasthttp
      command: ["go", "run", "cmd/fasthttp/main.go"]
      port: 8081
  - name: gin
    url: http://localhost:8082
    server:
      name: gin
      command: ["go", "run", "cmd/gin/main.go"]
      port: 8082
```

## CLI Usage

### Commands

```bash
# Run tests from configuration
wrk-runner test -c config.json

# Quick single URL test
wrk-runner quick https://api.example.com

# Create sample configuration
wrk-runner create-config

# Validate configuration
wrk-runner validate config.json
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `-d, --duration` | Test duration in seconds | 30 |
| `-c, --connections` | Number of connections | 1000 |
| `-t, --threads` | Number of threads | 8 |
| `-w, --warmup` | Warmup time in seconds | 5 |
| `-o, --output` | Output directory | results |
| `-s, --lua-script` | Lua script for wrk | None |
| `--verbose` | Enable verbose logging | False |

## Advanced Usage

### Custom Lua Scripts

Create a Lua script for custom request handling:

```lua
-- scripts/post.lua
wrk.method = "POST"
wrk.body = '{"key": "value"}'
wrk.headers["Content-Type"] = "application/json"
```

Use in configuration:

```json
{
  "lua_script": "scripts/post.lua",
  "tests": [...]
}
```

### Testing External APIs

```json
{
  "tests": [
    {
      "name": "external_api",
      "url": "https://api.github.com/users/octocat",
      "server": null
    }
  ]
}
```

### Multiple Endpoints

```json
{
  "tests": [
    {
      "name": "users_get",
      "url": "http://localhost:3000/users",
      "server": {...}
    },
    {
      "name": "users_post",
      "url": "http://localhost:3000/users",
      "server": null
    }
  ]
}
```

## Output

### Generated Files

- `results/wrk_{name}_{timestamp}.txt` - Raw wrk output
- `results/wrk_{name}_{timestamp}.json` - Parsed metrics in JSON
- `results/performance_report_{timestamp}.md` - Summary report

### Report Format

```markdown
# Performance Test Report
*Generated on 2024-01-01T12:00:00*

## Test Configuration
- Duration: 30s
- Connections: 1000
- Threads: 8
- Warmup: 5s

## Results

### my_api
**URL**: http://localhost:3000/api/v1/users
**Requests/sec**: 12345.67
**Transfer/sec**: 2.34MB

```
Running 30s test @ http://localhost:3000/api/v1/users
  8 threads and 1000 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     1.23ms    2.34ms  12.34ms   95.67%
    Req/Sec     1.54k   234.56    2.34k    85.67%
  37029 requests in 30.00s, 5.67MB read
Requests/sec:   1234.56
Transfer/sec:    193.45KB
```
```

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/droxer/wrk-runner
cd wrk-runner

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Install pre-commit hooks
uv run pre-commit install
```

### Running Tests

```bash
# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=wrk_reporter

# Run linting
uv run ruff check .
uv run black --check .

# Type checking
uv run mypy src/
```

### Building Documentation

```bash
# Install docs dependencies
uv sync --extra docs

# Serve documentation locally
uv run mkdocs serve

# Build documentation
uv run mkdocs build
```

## Requirements

- **wrk** - The load testing tool
- **Python 3.8+**

Install wrk:
- macOS: `brew install wrk`
- Ubuntu: `sudo apt-get install wrk`
- From source: https://github.com/wg/wrk

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

## Support

- [GitHub Issues](https://github.com/droxer/wrk-runner/issues)
- [Documentation](https://wrk-runner.readthedocs.io)
- [Discussions](https://github.com/droxer/wrk-runner/discussions)