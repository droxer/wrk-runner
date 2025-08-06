-- POST request with JSON body for login flow testing
-- Usage: wrk-runner test https://api.com -s post_login.lua -d 60 -c 500

wrk.method = "POST"
wrk.body = '{"username": "testuser", "password": "testpass"}'
wrk.headers["Content-Type"] = "application/json"
wrk.headers["Accept"] = "application/json"

-- Counter for successful logins
local counter = 0
local token = nil

-- Initialize request setup
request = function()
    -- If we have a token, use it in subsequent requests
    if token then
        wrk.headers["Authorization"] = "Bearer " .. token
        -- Test authenticated endpoint
        return wrk.format("GET", "/api/user/profile")
    else
        -- Initial login request
        return wrk.format("POST", "/api/auth/login")
    end
end

-- Process response
response = function(status, headers, body)
    if status == 200 then
        -- Extract session token from login response
        if not token then
            token = string.match(body, '"token":"([^"]+)"')
            if token then
                counter = counter + 1
            end
        end
    end
end

-- Report custom metrics
done = function(summary, latency, requests)
    io.write("\n=== Login Flow Results ===\n")
    io.write("Successful logins: " .. counter .. "\n")
    io.write("Total requests: " .. summary.requests .. "\n")
    io.write("Success rate: " .. (counter / summary.requests * 100) .. "%\n")
end