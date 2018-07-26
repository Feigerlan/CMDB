#coding:utf-8

import requests



url = "https://passport.5i5j.com/passport/login?service=https%3A%2F%2Fbj.5i5j.com%2Freglogin%2Findex%3FpreUrl%3Dhttps%253A%252F%252Fbj.5i5j.com%252F&status=1&city=bj"

header = {
    "Referer":"http://bj.5i5j.com/",
    "response":"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Mobile Safari/537.36"
}

session = requests.session()

requests = session.get(url = url ,headers =header)

response = requests.content.decode()

login_data = {
    "username":"18908087891"
}





