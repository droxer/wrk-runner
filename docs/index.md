# wrk-runner

Welcome to **wrk-runner**, a generic performance testing framework built on top of the powerful [wrk](https://github.com/wg/wrk) HTTP benchmarking tool.

## What is wrk-runner?

wrk-runner provides a modern, Python-based interface for wrk that makes load testing HTTP servers and APIs simple and configurable. It offers:

- **Easy configuration** via JSON/YAML files
- **Rich, colorful output** with detailed reports
- **Automatic server management** for local testing
- **Multiple output formats** (JSON, CSV, Markdown)
- **Cross-platform compatibility**
- **Extensible architecture**

## Quick Start

### 1. Install wrk-runner

```bash
pip install wrk-runner
```

### 2. Install wrk (if not already installed)

```bash
# macOS
brew install wrk

# Ubuntu/Debian
sudo apt-get install wrk

# From source
# See https://github.com/wg/wrk
```

### 3. Quick Test

```bash
# Test any URL
wrk-runner https://httpbin.org/get
```

### 4. Configuration-based Testing

```bash
# Create sample configuration
wrk-runner --create-sample

# Edit configuration file
vim performance_config.json

# Run tests
wrk-runner
```

## Key Features

### 🎯 Simple Configuration

Define your tests in JSON or YAML:

```yaml
duration: 30
connections: 1000
threads: 8
tests:
  - name: my_api
    url: http://localhost:3000/api/users
    server:
      name: nodejs_app
      command: ["npm", "start"]
      port: 3000
```

### 📊 Rich Output

Get beautiful, informative output:

```
✓ Performance testing complete!
📊 Report: results/performance_report_20240101_120000.md

┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Server     ┃ URL                          ┃ Requests/sec ┃ Transfer/sec ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ my_api     │ http://localhost:3000/users  │ 12345.67     │ 2.34MB       │
└────────────┴──────────────────────────────┴──────────────┴──────────────┘
```

### 🔧 Flexible Testing

- **Quick tests**: Single URL testing
- **Configuration tests**: Complex test suites
- **External APIs**: Test any HTTP endpoint
- **Local servers**: Automatic server management
- **Custom scripts**: Lua scripts for advanced scenarios

## Example Use Cases

### 1. API Performance Testing

```bash
# Test REST API endpoints
wrk-runner https://api.example.com/v1/users

# With custom parameters
wrk-runner https://api.example.com/v1/users -d 60 -c 2000 -t 16
```

### 2. Microservice Testing

```yaml
# config.yaml
duration: 60
connections: 5000
threads: 16
tests:
  - name: user_service
    url: http://localhost:8080/users
    server:
      name: user_service
      command: ["python", "user_service.py"]
      port: 8080
  
  - name: auth_service
    url: http://localhost:8081/auth
    server:
      name: auth_service
      command: ["node", "auth_service.js"]
      port: 8081
```

### 3. Load Testing Web Applications

```bash
# Test web application
wrk-runner https://myapp.com -d 300 -c 10000 -t 32
```

## Next Steps

- 📖 **Read the [Installation Guide](installation.md)**
- 🚀 **Follow the [Quick Start Tutorial](quickstart.md)**
- 📋 **Explore [Configuration Options](configuration.md)**
- 🔍 **Check out [Examples](examples.md)**

## Requirements

- **Python 3.8+**
- **wrk** - HTTP benchmarking tool
- **Click** - Command-line interface
- **Rich** - Beautiful terminal output
- **Pydantic** - Data validation

## License

MIT License - see [LICENSE](../LICENSE) for details.