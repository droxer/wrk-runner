# Lua Script Examples

This directory contains example Lua scripts for wrk-runner demonstrating various testing scenarios.

## Scripts Overview

### 1. post_login.lua
**Purpose**: Test login flow with session management
- POST login request with JSON credentials
- Extract and use authentication token
- Track successful logins
- Test authenticated endpoints

**Usage**:
```bash
wrk-runner test https://api.example.com -s post_login.lua -d 60 -c 500
```

### 2. get_with_params.lua
**Purpose**: Dynamic GET requests with URL parameters
- Cycle through user IDs
- Add query parameters dynamically
- Log errors for debugging
- Track performance metrics

**Usage**:
```bash
wrk-runner test https://api.example.com -s get_with_params.lua -d 30 -c 200
```

## Custom Scripting Guide

### Basic Structure
```lua
-- Request setup
request = function()
    return wrk.format(method, path, headers, body)
end

-- Response handling
response = function(status, headers, body)
    -- Process response data
end

-- Final report
done = function(summary, latency, requests)
    -- Custom metrics
end
```

### Available Variables
- `wrk.method`: HTTP method
- `wrk.headers`: Request headers table
- `wrk.body`: Request body
- `wrk.scheme`: HTTP/HTTPS
- `wrk.host`: Target host
- `wrk.port`: Target port
- `wrk.path`: Request path

### Global Functions
- `wrk.format(method, path, headers, body)`: Format HTTP request
- `os.getenv(name)`: Access environment variables
- `math.random()`: Generate random numbers
- `string.match()`: Pattern matching

## Advanced Examples

For more complex scenarios, you can:
- Load external data files
- Implement state machines
- Generate realistic user flows
- Track custom metrics per endpoint
- Validate response data