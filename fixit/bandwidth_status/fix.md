## 修改方法
* 修改 /usr/lib/lua/controller/admin/status.lua 文件
* 对 iface 对应的值进行过滤,使用 shellquote 函数对参数进行转义和过滤，以防止命令注入
* ```lua
    function action_bandwidth(iface)
        luci.http.prepare_content("application/json")
        function filterKeywords(str)
            local keywords = {"cat", "less", "more"}
            
            for _, keyword in ipairs(keywords) do
            str = string.gsub(str, keyword, "")
            end
            
            return str
        end
        # 修改前
        local bwc = io.popen("luci-bwc -i %q 2>/dev/null"
            % filterKeywords(iface))
        # 修改后
        local bwc = io.popen("luci-bwc -i %s 2>/dev/null"
            % luci.util.shellquote(iface))
        if bwc then
            luci.http.write("[")

            while true do
                local ln = bwc:read("*l")
                if not ln then break end
                luci.http.write(ln)
            end

            luci.http.write("]")
            bwc:close()
        end
    end
```