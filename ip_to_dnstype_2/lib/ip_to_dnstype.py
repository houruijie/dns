import requests
import json
from service import Service
import os


sv = Service("ip_to_dnstype", "ip_to_dnstype1")

def item_to_ip(item):
    return item['input']


@sv.handle_input_items(time_out=4)
def handle_items(request_items, config):
    ip_list = map(item_to_ip, request_items)

    form = {
        'ip_list': ','.join(ip_list)
    }
    url = os.environ['DNS_JUDGE_URL']
    #url = 'http://10.236.182.25:5000/'
    resp = requests.post(url=url, data=form)
    judge_result = json.loads(resp.content, encoding='gbk')

    inputs = judge_result.keys()
    result = []
    for input in inputs:
        dict = {
            'input':input,
            'output':[judge_result[input]],
            'error_info':None
        }
        result.append(dict)

    return result

# @sv.health_check()
# def health_check(request):
#     return json({
#         "status": "health",
#         "infor": "wwwww"
#     })

# print("the process is "+str(__name__))


sv.run()











# def ip_to_item(ip):
#     dict = {
#         'input':ip,
#         'output':None,
#         'error_info':None
#     }
#     return dict
#
# # # if __name__ == "__main__":
# # #     ip_list= ['111.38.102.67', '8.8.8.8']
# # #     judge_result=judge_DNS(ip_list)
# # #     print judge_result
# if __name__ == '__main__':
#     ip_list = ['8.8.8.8','120.79.50.45','2.2.2.2']
#     items = map(ip_to_item,ip_list)
#     print(items)
#     handle_items(items,{})
