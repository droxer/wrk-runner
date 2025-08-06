# Performance Testing with Python

This document explains how to use the new generic Python performance testing script (`performance_test.py`) which replaces the old bash script.

## Key Improvements

- **Generic**: Works with any servers, not just c10k-go
- **Configurable**: Uses JSON configuration files
- **Extensible**: Easy to add new servers and endpoints
- **Cross-platform**: Works on Windows, macOS, and Linux
- **Better error handling**: More robust and informative
- **JSON output**: Structured results for further processing

## Quick Start

1. **Install dependencies**:
   ```bash
   # Install wrk
   # macOS: brew install wrk
   # Ubuntu: sudo apt-get install wrk
   # From source: https://github.com/wg/wrk
   ```

2. **Create sample configuration**:
   ```bash
   ./performance_test.py --create-sample
   ```

3. **Run tests**:
   ```bash
   ./performance_test.py
   ```

## Configuration

### Basic Configuration

Create a JSON configuration file (e.g., `performance_config.json`):

```json
{
  "duration": 30,
  "connections": 1000,
  "threads": 8,
  "warmup": 5,
  "output_dir": "results",
  "tests": [
    {
      "name": "my_server",
      "url": "http://localhost:8080",
      "server": {
        "name": "myapp",
        "command": ["python", "app.py"],
        "port": 8080
      }
    }
  ]
}
```

### Advanced Configuration

For testing external APIs or multiple endpoints:

```json
{
  "duration": 60,
  "connections": 2000,
  "threads": 16,
  "warmup": 10,
  "output_dir": "results",
  "lua_script": "scripts/custom.lua",
  "tests": [
    {
      "name": "local_api",
      "url": "http://localhost:3000/api/v1/users",
      "server": {
        "name": "nodejs_api",
        "command": ["npm", "start"],
        "port": 3000,
        "env": {"NODE_ENV": "production"}
      }
    },
    {
      "name": "external_service",
      "url": "https://api.example.com/health",
      "server": null
    }
  ]
}
```

## Command Line Options

```bash
./performance_test.py [OPTIONS]

Options:
  -c, --config FILE     Configuration file (default: performance_config.json)
  -d, --duration SEC    Test duration in seconds
  --connections NUM     Number of connections
  --threads NUM         Number of threads
  -w, --warmup SEC      Warmup time in seconds
  -o, --output DIR      Output directory
  -s, --lua-script FILE Lua script for wrk
  --create-sample       Create sample configuration file
  -h, --help            Show help message
```

## Examples

### Test c10k-go servers (like original script)
```bash
# Using default configuration
./performance_test.py

# Override parameters
./performance_test.py -d 60 -c 2000 --threads 16
```

### Test custom servers
```bash
# Create configuration
./performance_test.py --create-sample

# Edit configuration file
vim performance_config.json

# Run tests
./performance_test.py
```

### Test external APIs
```bash
# Create advanced configuration
./performance_test.py --create-sample

# Edit advanced_config.json to test external services
./performance_test.py -c advanced_config.json
```

### Multiple test scenarios
```bash
# Run specific configuration
./performance_test.py -c configs/production.json

# Override output directory
./performance_test.py -c configs/staging.json -o staging_results
```

## Output

The script generates:

1. **Raw wrk output**: `results/wrk_{name}_{timestamp}.txt`
2. **Parsed metrics**: `results/wrk_{name}_{timestamp}.json`
3. **Summary report**: `results/performance_report_{timestamp}.md`
4. **Structured data**: JSON format for programmatic use

## Migration from Bash Script

### Original bash usage:
```bash
./performance_test.sh fasthttp -d 60 -c 2000
./performance_test.sh all -d 120 -c 5000 -t 16
```

### New Python usage:
```bash
# Use provided sample configuration
./performance_test.py -d 60 -c 2000
./performance_test.py -d 120 -c 5000 --threads 16
```

## Configuration Schema

### Server Configuration
- `name`: Server identifier (used in filenames)
- `command`: Command to start server (array or string)
- `port`: Port number to wait for
- `host`: Host to wait for (default: localhost)
- `env`: Environment variables (optional)

### Test Configuration
- `name`: Test identifier
- `url`: URL to test
- `server`: Server configuration (null for external APIs)

### Global Configuration
- `duration`: Test duration in seconds
- `connections`: Number of concurrent connections
- `threads`: Number of threads
- `warmup`: Warmup time in seconds
- `output_dir`: Output directory
- `lua_script`: Lua script for custom wrk behavior

## Troubleshooting

### Common Issues

1. **wrk not found**: Install wrk using system package manager
2. **Server fails to start**: Check server logs and configuration
3. **Port conflicts**: Ensure ports are available
4. **Permission errors**: Check file permissions for output directory

### Debug Mode
Enable debug logging by setting environment variable:
```bash
export PYTHONPATH=/path/to/script
python -m pdb performance_test.py
```

## Extending the Script

### Adding New Server Types
Simply add new server configurations to the JSON file:

```json
{
  "name": "new_server",
  "url": "http://localhost:9000",
  "server": {
    "name": "newapp",
    "command": ["java", "-jar", "app.jar"],
    "port": 9000,
    "env": {"JAVA_OPTS": "-Xmx1g"}
  }
}
```

### Custom Lua Scripts
Create Lua scripts for custom wrk behavior:

```lua
-- scripts/post.lua
wrk.method = "POST"
wrk.body = '{"key": "value"}'
wrk.headers["Content-Type"] = "application/json"
```

Then reference in configuration:
```json
{
  "lua_script": "scripts/post.lua"
}
```