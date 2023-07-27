import requests
import argparse

def check(args):
    address = args.address
    username = args.username
    password = args.password
    session = requests.Session()
    url = 'http://%s/cgi-bin/luci/' % address
    data = {'luci_username':username,'luci_password':password}
    response = session.post(url=url,data=data,verify=False)
    if (response.status_code == 200) or (response.status_code == 403):
        print("success")
    else:
        print("Fail")
def main():
    parser = argparse.ArgumentParser(description='cve-2019-12272.py')
    requiredNamed = parser.add_argument_group('required named arguments')
    requiredNamed.add_argument('-a', '--address', help='Luci host address', required=True)
    requiredNamed.add_argument('-u', '--username', help='Luci username', required=True)
    requiredNamed.add_argument('-p', '--password', help='Luci password', required=True)
    args = parser.parse_args()
    check(args)
if __name__== "__main__":
    main()
