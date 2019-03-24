# -*- coding: utf-8 -*-
from service import Service
from sanic.response import json
import time
import json
import requests
from retrying import retry
import os

#domain_analysis_url = "http://127.0.0.1/7777/batch"
domain_analysis_url = os.environ['DNS_URL']
#os.environ['DNS_DB_IP']
RETRY_TIMES = 3
RETRY_TIME_UNIT = 1000

sv = Service("domain_to_ip", "domain_to_ip1")

@retry(stop_max_attempt_number = RETRY_TIMES, wait_exponential_multiplier=RETRY_TIME_UNIT, wait_exponential_max=RETRY_TIME_UNIT)
def analyse_domain(domain, mode):
    '''
    :param domain:
    :param mode:
    :return:
    '''
    para = {'domain':domain,'type':'all','mode':mode}
    response = requests.get(domain_analysis_url, params=para, timeout=10)     # 超时？　网络原因？　重试３次的问题
    try:
        results = response.json()
    except:
        raise Exception("Internal Server Error:The server encountered an internal error "
                        "and was unable to complete your request.Either the server is "
                        "overloaded or there is an error in the application.")
    type_list = ['A', 'AAAA']  # 提取放回数据中的记录类型列表
    output = list()       # 返回计算结果列表
    for result in results['results']:    # 对于返回结果列表中的每一个结果
        for type in type_list:           #  对于我们要查的每一个记录，即Ａ记录，AAAA记录
            try:
                for subresult in result[type]:   # 对result[type]中的每一个子记录
                    for answer in subresult['answer list']:   # 对answer list中的每一个子记录，即真正记录结果的记录
                        output.append(answer['data'])   # 将记录类型和记录结果添加到output列表中

            except:
                continue
    return output

@sv.handle_input_item(strategy="thread",  pool_size=5, time_out=20)
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
        temp_ouput = analyse_domain(temp_input, mode)
        single_request_item["output"] = temp_ouput
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



