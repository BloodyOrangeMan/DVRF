## 修改方法
* 修改 `/usr/lib/lua/controller/admin/upload.lua` 文件,在 action_untar 函数中增加检查功能
* 检查解压后的目录有没有ln文件，有的话删除，防止软链接
```lua
-- Check for symlinks in /tmp/upload/ and remove them
for _, file in ipairs(fs.dir("/tmp/upload/")) do
    local stat = fs.stat("/tmp/upload/" .. file)
    if stat and stat.type == "link" then
        fs.unlink("/tmp/upload/" .. file)
    end
end
```