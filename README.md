# wrk-runner

Generic performance testing using wrk.

- **Easy CLI**: One-command testing with `wrk-runner https://api.com`
- **JSON/YAML Config**: Structured test definitions with servers, endpoints, and parameters
- **Rich Reports**: Auto-generated markdown reports with metrics and charts
- **Server Management**: Built-in server startup/shutdown for testing local apps
- **Multiple Formats**: JSON, CSV, HTML reports for CI/CD integration
- **Lua Support**: Custom scripts for complex testing scenarios

## Install

```bash
pip install wrk-runner
```

## Usage

```bash
# Quick test
wrk-runner https://httpbin.org/get  

# With options
wrk-runner https://httpbin.org/get -d 60 -c 1000 -t 8

# From config
wrk-runner -c config.json

# CLI commands
wrk-runner test -c config.json     # Run from config
wrk-runner quick https://httpbin.org/get   # Quick test
wrk-runner create-config           # Generate sample config
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