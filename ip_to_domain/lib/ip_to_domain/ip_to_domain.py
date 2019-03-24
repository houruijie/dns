# -*- coding: utf-8 -*-
from service import Service
from sanic.response import json
import time
import json
import requests
from retrying import retry
import os

#ANALYSE_PTR_URL = "http://127.0.0.1/7777/batch"
ANALYSE_PTR_URL = os.environ['DNS_URL']
RETRY_TIMES = 3
RETRY_TIME_UNIT = 1000
PTR_TIMEOUT = 10


sv = Service("ip_to_domain", "ip_to_domain1")

@retry(stop_max_attempt_number = RETRY_TIMES, wait_exponential_multiplier=RETRY_TIME_UNIT, wait_exponential_max=RETRY_TIME_UNIT)
def analyse_ptr(domain_ip, mode):
    '''
    Get list of domains whose server IP address is domain_ip

    :param domain_ip: the input data about domain IP address
    :param mode: Conditions for Query End. if no new results are added continuous mode DNS query, stop querying.
    :return: Returns a list of results, each result in the list is a domain name and its type is string
    '''

    para = {}
    para['domain'] = domain_ip
    para['type'] = 'ptr'
    para['mode'] = mode
    response = requests.get(ANALYSE_PTR_URL, params=para,timeout= PTR_TIMEOUT)
    try:
        results = json.loads(response.content)
    except:
        raise Exception("Internal Server Error:The server encountered an internal error "
                        "and was unable to complete your request.Either the server is "
                        "overloaded or there is an error in the application.")
    output = list()       # 返回计算结果列表
    for result in results['results']:    # 对于返回结果列表中的每一个结果
        try:
            for subresult in result['PTR']:   # 对result[type]中的每一个子记录
                for answer in subresult['answer list']:   # 对answer list中的每一个子记录，即真正记录结果的记录
                    output.append(answer['data'])   # 将记录类型和记录结果添加到output列表中

        except:
            continue
    return output

@sv.handle_input_item(strategy="thread",  pool_size=5, time_out=2)
def handle_item(single_request_item, config):
    '''
    Main Control Flow for Item Processing
    :param single_request_item: single_request_item is a map such as:
                                {
                                    "input":2,
                                    "output":None,
                                    "error_info":None
                                }
                                input -- the data need to be done
                                output-- the output of the input
                                error_info  -- the info of the error
    :param config: Configuration information needed to process item
    '''

    temp_input = single_request_item["input"]
    mode = config.get('mode',5)
    try:
        single_request_item["output"] = analyse_ptr(temp_input, mode)
    except Exception as e:
        single_request_item["error_info"] = e
    return single_request_item


# @sv.health_check()
# def health_check(request):
#     return json({
#         "status": "health",
#         "infor": "wwwww"
#     })

sv.run()






# if __name__ == "__main__":
#     try:
#         output = ptr_analysis('1.2.4.8',3)
#         print(output)
#     except Exception as e:
#         print(e)
