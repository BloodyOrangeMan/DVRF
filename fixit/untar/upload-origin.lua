module("luci.controller.admin.upload", package.seeall)

function index()
	local fs = require "nixio.fs"

	entry({"admin", "upload"}, alias("admin", "upload", "upload"), _("Upload"), 30).index = true

	entry({"admin", "upload", "upload"}, call("action_upload"), _("Upload"), 1)

	-- call() instead of post() due to upload handling!
    entry({"admin", "upload", "upload", "untar"}, call("action_untar"))
	entry({"admin", "upload", "upload", "uploadflag"}, call("action_uploadflag"))
    entry({"admin", "upload", "upload", "sendfiles"}, call("action_sendfiles"))
    entry({"admin", "upload", "upload", "sendfiles2"}, call("action_sendfiles2"))
    entry({"admin", "upload", "upload", "date"}, call("action_date")).leaf = true
end

local function supports_sysupgrade()
	return nixio.fs.access("/lib/upgrade/platform.sh")
end

local function supports_reset()
	return (os.execute([[grep -sq "^overlayfs:/overlay / overlay " /proc/mounts]]) == 0)
end

function action_upload()
	--
	-- Overview
	--
	luci.template.render("admin_upload/upload", {
		reset_avail   = supports_reset(),
		upgrade_avail = supports_sysupgrade()
	})
end

function action_uploadflag()
	local fs = require "nixio.fs"
	local http = require "luci.http"

    local c=http.formvalue("flag") 
    local file = io.open("/etc/config/samba", "r")

    -- 读取文件内容并逐行匹配
    local lineNum = 0
    local nextLine = ""
    local lastLine = false
    for line in file:lines() do
        lineNum = lineNum + 1
        if line == c then
            lastLine = lineNum
        end
    end

    -- 关闭文件
    file:close()

    -- 输出结果
    if lastLine then
        if lastLine==1 then
            hint='some URL can be used,want know more please using xss attack in port forwards'
        end
        if lastLine==2 then
            hint='Incredible! Now untar seems to be a good tool'
        end
        if lastLine==3 then
            hint='serialize is fun! learn the code to get flag'
            flag_3=true

        end
        if lastLine==4 then
            hint='you successfully find all flag in web,see if you can crack the pwn'
            flag_4=true
        end
        if lastLine==lineNum then
            os.execute('echo "flag{$(cat /dev/urandom | tr -dc "a-zA-Z0-9" | head -c 16)}" >> /etc/config/samba')
            if lastLine==1 or lastLine==2 then
                os.execute('tail -n 1 /etc/config/samba >/flag')
            end
            if lastLine==3 then
                os.execute('tail -n 1 /etc/config/samba >/www/flag')
            end
        end
        luci.template.render("admin_upload/upload", {
            flag_success = true,
            flag_hint=hint,
            flag_3=flag_3,
            flag_4=flag_4
    })
    else
        luci.template.render("admin_upload/upload", {
            flag_failed = true
    })
    end
    http.redirect(luci.dispatcher.build_url('admin/upload/upload'))
end

function action_sendfiles()
    local reader = ltn12_popen("cat /www/level4.zip")
    local http = require "luci.http"
    http.header(
        'Content-Disposition', 'attachment; filename="level4-%s-%s.zip"' %{
            luci.sys.hostname(),
            os.date("%Y-%m-%d")
        })

    http.prepare_content("application/x-targz")
    luci.ltn12.pump.all(reader, http.write)
    http.redirect(luci.dispatcher.build_url('admin/upload/upload'))
end
function action_sendfiles2()
    local reader = ltn12_popen("cat /www/level4.zip")
    local http = require "luci.http"
    http.header(
        'Content-Disposition', 'attachment; filename="level4-%s-%s.zip"' %{
            luci.sys.hostname(),
            os.date("%Y-%m-%d")
        })

    http.prepare_content("application/x-targz")
    luci.ltn12.pump.all(reader, http.write)
    http.redirect(luci.dispatcher.build_url('admin/upload/upload'))
end

function action_untar()
    local fs = require "nixio.fs"
	local http = require "luci.http"
    local c=http.formvalue("fileName") 
	local tarfile_tmp = "/tmp/upload/file.tar.gz"
	local fp
	http.setfilehandler(
		function(meta, chunk, eof)
			if not fp and meta then
				fp = io.open(tarfile_tmp, "w")
			end
			if fp and chunk then
				fp:write(chunk)
			end
			if fp and eof then
				fp:close()
			end

		end
	)

	if not luci.dispatcher.test_post_security() then
		fs.unlink(tarfile_tmp)
		return
	end

    if os.execute("tar -C /tmp/upload/ -xf %q >/dev/null 2>&1 && rm %q" % {tarfile_tmp, tarfile_tmp}) == 0 then
		luci.template.render("admin_upload/upload", {
			upload_success = true
		})
	else
		luci.template.render("admin_upload/upload", {
			upload_success = false
		})
	end
	return
	http.redirect(luci.dispatcher.build_url('admin/upload/upload'))
end

function action_date(code)
    local http = require("luci.http")
    local util = require("luci.util")
    local md5 = require ("luci.md5")
    -- 定义一个名为date的类
    local date = {
        a = nil,
        b = nil,
        file = nil
    }

    -- 定义date类的__wakeup方法
    function date:__wakeup()
        -- if type(self.a) == "table" or type(self.b) == "table" then
        --     http.status(400, "Bad Request")
        --     http.write("no array")
        --     return
        -- end
        -- json = require "luci.json"
        -- local base64 = require"luci.base64"
        -- local date = {
        --     a = {},
        --     b = {},
        --     file = "\\f\\l\\a\\g"
        -- }
        
        -- -- 创建一个函数来模拟PHP中的Error类
        -- local function Error(message, code)
        --     return {
        --         message = message,
        --         code = code
        --     }
        -- end
        
        -- -- 创建一个date对象，并设置a和b字段为Error对象
        -- date.a = Error("payload", 1)
        -- date.b = Error("payload", 2)
        -- -- 序列化date对象为字符串
        -- local serialized_str = json.encode(date)
        -- local encoded = base64.encode( serialized_str )


        if self.a ~= self.b and md5.sum(self.a) == md5.sum(self.b) then
            local content = self.file
            local uuid = util.exec("echo $RANDOM"):gsub("\n", "") .. ".txt"
            util.exec("echo '" .. content .. "' > " .. uuid)
            local data = util.exec("cat " .. uuid):gsub("%s+", "")
            -- http.write(encoded)
            http.write(util.exec("cat " .. data))
        else
            http.status(400, "Bad Request")
            http.write("")
        end
    end
    -- 解析传递的GET参数并调用date类的__wakeup方法
    http.prepare_content("application/json")
    json = require "luci.json"
    local base64 = require"luci.base64"
    if code then
        local decoded_code = base64.decode(code)
        local success, obj = pcall(json.decode, decoded_code)
        if success and type(obj) == "table" then
            setmetatable(obj, { __index = date })
            obj:__wakeup()
        else
            http.status(400, "Bad Request")
            http.write(decoded_code)
        end
    else
        http.status(400, "Bad Request")
        http.write("")
    end
end

function ltn12_popen(command)

	local fdi, fdo = nixio.pipe()
	local pid = nixio.fork()

	if pid > 0 then
		fdo:close()
		local close
		return function()
			local buffer = fdi:read(2048)
			local wpid, stat = nixio.waitpid(pid, "nohang")
			if not close and wpid and stat == "exited" then
				close = true
			end

			if buffer and #buffer > 0 then
				return buffer
			elseif close then
				fdi:close()
				return nil
			end
		end
	elseif pid == 0 then
		nixio.dup(fdo, nixio.stdout)
		fdi:close()
		fdo:close()
		nixio.exec("/bin/sh", "-c", command)
	end
end