-- Detailed performance testing script for wrk
-- Provides comprehensive metrics including latency distribution, status codes, and throughput

local counter = 1
local threads = {}

-- Setup function - called once per thread
function setup(thread)
    thread:set("id", counter)
    table.insert(threads, thread)
    counter = counter + 1
end

-- Initialize thread-specific variables
function init(args)
    local msg = "thread %d created"
    print(msg:format(id))
    
    -- Initialize counters
    responses = {}
    requests = 0
    bytes = 0
    start_time = 0
    end_time = 0
    
    -- Initialize latency buckets (in microseconds)
    latencies = {
        under_1ms = 0,
        under_2ms = 0,
        under_5ms = 0,
        under_10ms = 0,
        under_20ms = 0,
        under_50ms = 0,
        under_100ms = 0,
        under_200ms = 0,
        under_500ms = 0,
        under_1000ms = 0,
        over_1000ms = 0
    }
    
    -- Status code counters
    status_codes = {}
    for i = 100, 599 do
        status_codes[i] = 0
    end
end

-- Request function - called for each request
function request()
    requests = requests + 1
    if start_time == 0 then
        start_time = os.clock()
    end
    return wrk.request()
end

-- Response function - called for each response
function response(status, headers, body)
    end_time = os.clock()
    
    -- Count status codes
    if status_codes[status] then
        status_codes[status] = status_codes[status] + 1
    end
    
    -- Count bytes received
    if headers["Content-Length"] then
        bytes = bytes + tonumber(headers["Content-Length"])
    else
        bytes = bytes + #body
    end
    
    -- Calculate latency and bucket it
    local latency = (end_time - start_time) * 1000000  -- Convert to microseconds
    
    if latency < 1000 then
        latencies.under_1ms = latencies.under_1ms + 1
    elseif latency < 2000 then
        latencies.under_2ms = latencies.under_2ms + 1
    elseif latency < 5000 then
        latencies.under_5ms = latencies.under_5ms + 1
    elseif latency < 10000 then
        latencies.under_10ms = latencies.under_10ms + 1
    elseif latency < 20000 then
        latencies.under_20ms = latencies.under_20ms + 1
    elseif latency < 50000 then
        latencies.under_50ms = latencies.under_50ms + 1
    elseif latency < 100000 then
        latencies.under_100ms = latencies.under_100ms + 1
    elseif latency < 200000 then
        latencies.under_200ms = latencies.under_200ms + 1
    elseif latency < 500000 then
        latencies.under_500ms = latencies.under_500ms + 1
    elseif latency < 1000000 then
        latencies.under_1000ms = latencies.under_1000ms + 1
    else
        latencies.over_1000ms = latencies.over_1000ms + 1
    end
end

-- Done function - called when all requests are complete
function done(summary, latency, requests)
    local duration = summary.duration / 1000000  -- Convert to seconds
    local bytes_total = 0
    local requests_total = 0
    local responses_total = 0
    
    -- Aggregate results from all threads
    local all_status_codes = {}
    local all_latencies = {
        under_1ms = 0,
        under_2ms = 0,
        under_5ms = 0,
        under_10ms = 0,
        under_20ms = 0,
        under_50ms = 0,
        under_100ms = 0,
        under_200ms = 0,
        under_500ms = 0,
        under_1000ms = 0,
        over_1000ms = 0
    }
    
    -- Initialize status codes
    for i = 100, 599 do
        all_status_codes[i] = 0
    end
    
    -- Collect data from all threads
    for _, thread in ipairs(threads) do
        local tid = thread:get("id")
        
        -- Aggregate status codes
        for status, count in pairs(thread:get("status_codes")) do
            all_status_codes[status] = (all_status_codes[status] or 0) + count
        end
        
        -- Aggregate latencies
        local thread_latencies = thread:get("latencies")
        for bucket, count in pairs(thread_latencies) do
            all_latencies[bucket] = all_latencies[bucket] + count
        end
        
        bytes_total = bytes_total + thread:get("bytes")
        requests_total = requests_total + thread:get("requests")
    end
    
    -- Calculate totals
    responses_total = summary.requests
    
    -- Print detailed report
    print("\n=== DETAILED PERFORMANCE REPORT ===")
    print(string.format("Duration: %.2f seconds", duration))
    print(string.format("Total Requests: %d", responses_total))
    print(string.format("Total Bytes: %d", bytes_total))
    print(string.format("Throughput: %.2f requests/sec", responses_total / duration))
    print(string.format("Data Transfer: %.2f MB/sec", (bytes_total / duration) / (1024 * 1024)))
    
    print("\n=== LATENCY DISTRIBUTION ===")
    local total_responses = responses_total
    if total_responses > 0 then
        print(string.format("< 1ms:    %6d (%.2f%%)", all_latencies.under_1ms, (all_latencies.under_1ms / total_responses) * 100))
        print(string.format("< 2ms:    %6d (%.2f%%)", all_latencies.under_2ms, (all_latencies.under_2ms / total_responses) * 100))
        print(string.format("< 5ms:    %6d (%.2f%%)", all_latencies.under_5ms, (all_latencies.under_5ms / total_responses) * 100))
        print(string.format("< 10ms:   %6d (%.2f%%)", all_latencies.under_10ms, (all_latencies.under_10ms / total_responses) * 100))
        print(string.format("< 20ms:   %6d (%.2f%%)", all_latencies.under_20ms, (all_latencies.under_20ms / total_responses) * 100))
        print(string.format("< 50ms:   %6d (%.2f%%)", all_latencies.under_50ms, (all_latencies.under_50ms / total_responses) * 100))
        print(string.format("< 100ms:  %6d (%.2f%%)", all_latencies.under_100ms, (all_latencies.under_100ms / total_responses) * 100))
        print(string.format("< 200ms:  %6d (%.2f%%)", all_latencies.under_200ms, (all_latencies.under_200ms / total_responses) * 100))
        print(string.format("< 500ms:  %6d (%.2f%%)", all_latencies.under_500ms, (all_latencies.under_500ms / total_responses) * 100))
        print(string.format("< 1000ms: %6d (%.2f%%)", all_latencies.under_1000ms, (all_latencies.under_1000ms / total_responses) * 100))
        print(string.format("> 1000ms: %6d (%.2f%%)", all_latencies.over_1000ms, (all_latencies.over_1000ms / total_responses) * 100))
    end
    
    print("\n=== STATUS CODES ===")
    local status_counts = {}
    for status, count in pairs(all_status_codes) do
        if count > 0 then
            table.insert(status_counts, {status = status, count = count})
        end
    end
    
    -- Sort by status code
    table.sort(status_counts, function(a, b) return a.status < b.status end)
    
    for _, item in ipairs(status_counts) do
        print(string.format("%3d: %6d (%.2f%%)", item.status, item.count, (item.count / responses_total) * 100))
    end
    
    print("\n=== SUMMARY ===")
    print(string.format("Requests/sec: %.2f", responses_total / duration))
    print(string.format("Transfer/sec: %.2f MB", (bytes_total / duration) / (1024 * 1024)))
    
    -- Standard wrk latency stats
    print(string.format("Latency: %.2fms", (latency.mean / 1000)))
    print(string.format("Latency Stdev: %.2fms", (latency.stdev / 1000)))
    print(string.format("Latency Max: %.2fms", (latency.max / 1000)))
    
    -- Percentiles
    print(string.format("50%%: %.2fms", (latency:percentile(50) / 1000)))
    print(string.format("75%%: %.2fms", (latency:percentile(75) / 1000)))
    print(string.format("90%%: %.2fms", (latency:percentile(90) / 1000)))
    print(string.format("99%%: %.2fms", (latency:percentile(99) / 1000)))
    
    print("\n=== END REPORT ===")
end