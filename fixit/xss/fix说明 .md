## 修改方法
* 修改 /usr/lib/lua/model/cbi/firewall/forward-details.lua 文件
* 对 name 对应的值进行过滤
* ```lua
    -- 修改前
    m.title = "%s - %s" %{ translate("Firewall - Port Forwards"), name }
    -- 修改后
	m.title = "%s - %s" %{ translate("Firewall - Port Forwards"), luci.util.pcdata(name) }
```