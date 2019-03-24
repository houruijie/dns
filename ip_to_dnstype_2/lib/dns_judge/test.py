import requests
import json

form = {
    'ip_list': ','.join(['8.8.8.8','120.79.50.45','2.2.2.2'])
}

url = 'http://127.0.0.1:5000/'
resp = requests.post(url=url,data=form)
content = json.loads(resp.content,encoding='gbk')
print content