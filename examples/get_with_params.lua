-- GET request with dynamic URL parameters
-- Usage: wrk-runner test https://api.com -s get_with_params.lua -d 30 -c 200

-- Counter for requests
local counter = 0
local user_ids = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}

-- Setup headers
wrk.headers["Accept"] = "application/json"
wrk.headers["User-Agent"] = "wrk-runner"

request = function()
    counter = counter + 1
    local user_id = user_ids[(counter % #user_ids) + 1]
    local endpoint = "/api/users/" .. user_id
    
    -- Add query parameters
    local params = {
        include = "posts,comments",
        limit = math.random(5, 20)
    }
    
    local query = "?include=" .. params.include .. "&limit=" .. params.limit
    return wrk.format("GET", endpoint .. query)
end

-- Log response status for debugging
response = function(status, headers, body)
    if status >= 400 then
        io.write("Error: " .. status .. " for user " .. counter .. "\n")
    end
end

done = function(summary, latency, requests)
    io.write("\n=== GET Requests Summary ===\n")
    io.write("Total requests: " .. summary.requests .. "\n")
    io.write("Average latency: " .. (latency.mean / 1000) .. "ms\n")
end