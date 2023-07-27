## 修改方法
* 修改 `/usr/lib/lua/controller/admin/upload.lua` 文件,在 action_date 函数中增加检查功能
* 检查 传入的 a 和 b 不为数组，因为在md5.lua文件中，如果两者为数组则返回 none 值，由此可以绕开 md5 值的比较
```lua
        if type(self.a) == "table" or type(self.b) == "table" then
            http.status(400, "Bad Request")
            http.write("no array")
            return
        end
```