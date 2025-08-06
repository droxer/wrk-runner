# wrk-runner

Generic performance testing using wrk.

- **Easy CLI**: One-command testing with `wrk-runner test https://httpbin.org/get`
- **JSON/YAML Config**: Structured test definitions with endpoints and parameters
- **Rich Reports**: Auto-generated markdown reports with metrics and charts
- **Multiple Formats**: JSON, CSV, HTML reports for CI/CD integration
- **Lua Support**: Custom scripts for complex testing scenarios

## Install

```bash
pip install wrk-runner
```

## Usage

### CLI Commands
```bash
wrk-runner [COMMAND] [OPTIONS]

Commands:
  test [URL]       Quick test with URL or config file test
  create-config    Generate sample configuration
  validate FILE    Validate configuration file
  visualize        Scan and visualize results
```

### Quick Test
```bash
# Basic quick test
wrk-runner test https://httpbin.org/get

# With parameters
wrk-runner test https://api.com -d 60 -c 1000 -t 8 -w 5 -o results/
```

### Configuration Test
```bash
# JSON config
wrk-runner test -c config.json

# YAML config
wrk-runner test -c config.yaml

# Custom output
wrk-runner test -c config.json --output custom_results/

# Override config parameters
wrk-runner test -c config.json -d 60 -c 2000
```

### Options
```bash
-d, --duration SECONDS    Test duration (default: 30)
-c, --connections NUM     Number of connections (default: 1000)
-t, --threads NUM         Number of threads (default: 8)
-w, --warmup SECONDS      Warmup time (default: 5)
-o, --output DIR          Output directory (default: results)
-s, --lua-script FILE     Lua script for wrk
-f, --format FORMAT       Output format: html, json, md (default: md)
--verbose                 Enable verbose logging
--help                    Show help message
```

## Config

```json
{
  "duration": 30,
  "connections": 1000,
  "threads": 8,
  "tests": [
    {
      "name": "api",
      "url": "http://localhost:3000/api"
    }
  ]
}
```

## Dev Setup

```bash
git clone https://github.com/droxer/wrk-runner
cd wrk-runner
make install-dev
make check
```

## Make Commands

| Command | Description |
|---------|-------------|
| `make test` | Run tests |
| `make build` | Build package |
| `make publish` | Publish to PyPI |
| `make check` | Run all checks |
| `make all` | Full pipeline |

## Requirements
- Python 3.10+
- wrk (`brew install wrk`)

## License
MIT