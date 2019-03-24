# -*- coding: UTF-8 -*-
import MySQLdb
import sys
import os
#import DNS
from single_new import Single
from batch_new import Batch
import info
from flask import Flask, jsonify,request,Response
import collections
import datetime
import json

APP = Flask(__name__)


def byteify(input, encoding='utf-8'):
    if isinstance(input, dict):
        return {byteify(key): byteify(value) for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode(encoding)
    else:
        return input

@APP.route('/hello')#Instructions
def hello():
    current_path = os.path.abspath(__file__)
    father_path = os.path.abspath(os.path.dirname(current_path) + os.path.sep + ".")

    fr = open(father_path + '/region.txt', 'r')
    return open(father_path+r'/hello_latest.html', 'r').read()

# @APP.route('/test3')#Instructions
# def haha():
#     current_path = os.path.abspath(__file__)
#     father_path = os.path.abspath(os.path.dirname(current_path) + os.path.sep + ".")
#
#     fr = open(father_path + '/region.txt', 'r')
#     return open(father_path+r'/hello.html', 'r').read()


# @APP.route('/test')
# def test():
#     '''
#       路由测试
#     '''
#     res=[]
#     reload(sys)
#     sys.setdefaultencoding('utf8')
#
#     current_path = os.path.abspath(__file__)
#     # 获取当前文件的父目录
#     father_path = os.path.abspath(os.path.dirname(current_path) + os.path.sep + ".")
#     # config.ini文件路径,获取当前目录的父目录的父目录与congig.ini拼接
#     config_file_path = os.path.join(os.path.abspath(os.path.dirname(current_path) + os.path.sep + ".."), 'config.ini')
#     #print('当前目录:' + current_path)
#    # print('当前父目录:' + father_path)
#     #print('config.ini路径:' + config_file_path)
#
#     try:
#         fr=open(father_path+'/Readme.txt','r')
#     except IOError:
#         return jsonify("open file error")
#     while True:
#         line = fr.readline()
#         if line:
#             line=line.strip()
#             res.append(line)
#
#         else:
#             break
#     fr.close()
#     reload(sys)
#     sys.setdefaultencoding('utf8')
#     #print res
#     return jsonify(res)


    # image = file(father_path+"/1.jpg")
    # resp = Response(image, mimetype="image/jpg")
    # return resp

@APP.route('/single_old',methods=['post','get'])
def api_article2():
    reload(sys)
    sys.setdefaultencoding('utf8')


    domainname = request.args.get("domain", type=str)
    dns=request.args.get("dns",type=str)
    type = request.args.get("type", type=str)
    #data = request.args.get("data", type=str)

    id0="0"

    if domainname:

        domainname=domainname.lower()
        if domainname.find(".",0) <> -1:
            id0=domainname
        else:
            return "domainname input error"
        print id0
    else:
        id0="nodemands"

    #dns=dns.lower()
    if dns:
        if dns.find(".",0) <> -1:

            if len(dns.split("."))!=4:
                dns_error = {}
                dns_error['flag'] = "301"

                return jsonify(dns_error)

            id1="1"
        #elif dns.find("nodemands",0) <> -1:
            #id1="3"
        elif dns.find("中国",0)<>-1 or dns.find("*",0)<>-1:
            id1="2"
        else:
            dns_error={}
            dns_error['flag']="301"

            return jsonify(dns_error)
    else:
        id1="1"
        dns="47.94.47.91"


    if type:
        id=type.lower()
        # 处理参数2
        id2 = ""
        #print len(id)
        if id.find("a", 0) <> -1 and len(id)==1:
            id2 = id2 + "1"

        # if id.find("aaaa",0)<>-1 and id.find("a",id.find("aaaa",0)+1)<>-1:
        #     if id2.find("1",0)==-1:
        #         id2 = id2 + "1"
        if id.find("aaaa", 0) <> -1:
            id2 = id2 + "2"
        if id.find("cname", 0) <> -1:
            id2 = id2 + "3"
        if id.find("ns", 0) <> -1:
            id2 = id2 + "4"
        if id.find("mx", 0) <> -1:
            id2 = id2 + "5"
        if id.find("soa", 0) <> -1:
            id2 = id2 + "6"
        if id.find("txt", 0) <> -1:
            id2 = id2 + "7"


        #print id2
    else:
        id2="1"
    if id2 == "":
        type_error = {}
        type_error['flag'] = "302"

        return jsonify(type_error)
    # 处理参数3
    # if data:
    #     id3 = ""
    #     id = data.lower()
    #     if id.find("header", 0) <> -1:
    #         id3 = id3 + "2"
    #     if id.find("answer", 0) <> -1:
    #         id3 = id3 + "3"
    #     if id.find("authority", 0) <> -1:
    #         id3 = id3 + "4"
    #     if id.find("additional", 0) <> -1:
    #         id3 = id3 + "5"
    #     if id.find("all", 0) <> -1:
    #         id3 = "2345"
    #     # if id.find("querytime", 0) <> -1:
    #     #     id3 = id3 + "6"
    #     # if id.find("nodemands", 0) <> -1:
    #     #     id3 = id3 + "1"
    #
    #     #print id3
    # else:
    #     data="all"
    #     id3 = "2345"
    # if id3 == "":
    #     data_error = {}
    #     data_error['flag'] = "303"

        return jsonify(data_error)

    appoint = ""
    # get dns
    #if id1 == "1":

    if id1 == "2":
        appoint=dns
    print dns+"   "+appoint
    reload(sys)
    sys.setdefaultencoding('utf8')
    instance2 = MyTest2(id0,id1, id2, dns, appoint)
    result = {}
    result = collections.OrderedDict()
    result = instance2.output()
    #return jsonify(result)
    if result=="error":
        dns_error = {}
        dns_error['flag'] = "301"

        return jsonify(dns_error)
    else:
        return jsonify(result)
        return Response(json.dumps(result),mimetype='application/json')


# @APP.route('/batch',methods=['post','get'])
# def api_article3():
#     reload(sys)
#     sys.setdefaultencoding('utf8')
#
#     domainname = request.args.get("domain", type=str)
#
#     domainname=domainname.lower()
#
#     mode=request.args.get("mode",type=str)
#     result = {}
#     if mode.isdigit():
#         vital_num = int(mode)
#         if vital_num > 1000:
#             result['error'] = '对不起，您的mode输入不正确！mode请输入不超过1000的正整数！'
#             return jsonify(result)
# #    elif mode == 'fast':
#         vital_num = 10
# #    elif mode == 'full':
#         vital_num = 20
#     else:
#         result['error'] = '对不起，您的mode输入不正确！mode请输入不超过1000的正整数！'
#         return jsonify(result)
#
#     reload(sys)
#     sys.setdefaultencoding('utf8')
#     instance3 = MyTest3(domainname,vital_num)
#     result = instance3.output()
#
#     return jsonify(result)

@APP.route('/single',methods=['post','get'])
def api_single():
    reload(sys)
    sys.setdefaultencoding('utf8')

    domainname = request.args.get("domain", type=str)

    dns = request.args.get("dns", type=str)

    typename = request.args.get("type", type=str)

    if domainname:
        domainname = domainname.lower()
    else:
        domainname = 'www.baidu.com'

    if dns:
        pass
    else:
        dns = '47.94.47.91'

    if typename:
        typename = typename.upper()
    else:
        typename = 'A'


    country, prov, city, isp = info.find_info(dns)

    info_dict = {
        'domain': domainname,
        'dns': dns,
        'country': country,
        'province': prov,
        'city': city,
        'isp': isp,
        'current time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }

    result = {}
    result_list = []

    if typename != 'ALL':
        reload(sys)
        sys.setdefaultencoding('utf8')
        # if domainname.count('.') == 1:
        #     if typename == 'AAAA'
        # elif domainname.count('.') == 2 and domainname.find('.com.cn') != -1:
        instance = Single(domainname,dns,typename)
        subresult = instance.output()
        result_list.append(subresult)

    else:
        reload(sys)
        sys.setdefaultencoding('utf8')
        type_list = ['A', 'AAAA', 'CNAME', 'MX', 'NS', 'SOA', 'TXT']

        for typestr in type_list:
            instance = Single(domainname, dns, typestr)
            subresult = instance.output()
            result_list.append(subresult)

    result['results'] = result_list
    #print result
    #reload(sys)
    #sys.setdefaultencoding('utf8')
    result = dict(info_dict.items() + result.items())
    return jsonify(result)

@APP.route('/batch',methods=['post','get'])
def api_batch():
    reload(sys)
    sys.setdefaultencoding('utf8')

    domainname = request.args.get("domain", type=str)
    domainname=domainname.lower()

    typename = request.args.get("type", type=str)
    typename = typename.upper()

    mode=request.args.get("mode",type=str)
    result = {}

    if mode.isdigit():
        vital_num = int(mode)
        if vital_num > 1000:
            result['error'] = '对不起，您的mode输入不正确！mode请输入不超过1000的正整数！'
            return jsonify(result)
    else:
        result['error'] = '对不起，您的mode输入不正确！mode请输入不超过1000的正整数！'
        return jsonify(result)
    result_list = []
    if typename != 'ALL':
        reload(sys)
        sys.setdefaultencoding('utf8')
        # if domainname.count('.') == 1:
        #     if typename == 'AAAA'
        # elif domainname.count('.') == 2 and domainname.find('.com.cn') != -1:
        instance = Batch(domainname,typename,vital_num)
        subresult = instance.output()
        result_list.append(subresult)
    else:
        reload(sys)
        sys.setdefaultencoding('utf8')
        type_list = ['A', 'AAAA', 'CNAME', 'MX', 'NS', 'SOA', 'TXT']
        #cn_list = ['.ac.cn', '.com.cn', '.org.cn', 'net.cn', '.gov.cn', '.mil.cn', '.edu.cn']
        # if domainname.count('.') == 1:
        #     type_list = ['A','MX','NS','SOA','TXT']
        # elif domainname.count('.') == 2:
        #     if domainname.find('.com.cn') != -1 or domainname.find('.edu.cn') != -1:
        #         type_list = ['A', 'MX', 'NS', 'SOA', 'TXT']
        #     else:
        #         type_list = ['A', 'AAAA', 'CNAME']
        # else:
        #     type_list = ['A', 'AAAA', 'CNAME']

        for typestr in type_list:
            instance = Batch(domainname,typestr,vital_num)
            subresult = instance.output()
            result_list.append(subresult)
    result['domain'] = domainname
    result['current time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    result['results'] = result_list
    #print result
    #reload(sys)
    #sys.setdefaultencoding('utf8')
    return jsonify(result)

# @APP.route('/test/<articleid>')
# def api_article(articleid):
#     reload(sys)
#     sys.setdefaultencoding('utf8')
#     id=articleid
#     idd=str(id)
#
#     begin=idd.find(';',0)
#     end=idd.find(';',begin+1)
#
#     parameter1=idd[0:begin]
#     parameter2=idd[begin+1:end]
#     parameter3=idd[end+1:]
#
#     #处理参数1
#     id = parameter1.lower()
#     if id.find("load", 0) <> -1:
#         id1="1"
#         print id1
#     elif id.find("appoint", 0) <> -1:
#         id1="2"
#         print id1
#     elif id.find("no demands", 0) <> -1:
#         id1="3"
#         print id1
#     else:
#         return "error1"
#
#     #处理参数2
#     id2=""
#     id = parameter2.lower()
#     print len(id)
#     if id.find("a", 0) <> -1:
#         if len(id)==1:
#             id2 = id2 + "1"
#         elif id[id.find("a",0)+1]<>"a":
#             id2 =id2+ "1"
#
#     # if id.find("aaaa",0)<>-1 and id.find("a",id.find("aaaa",0)+1)<>-1:
#     #     if id2.find("1",0)==-1:
#     #         id2 = id2 + "1"
#     if id.find("aaaa", 0) <> -1:
#         id2 = id2 + "2"
#     if id.find("cname", 0) <> -1:
#         id2 = id2 + "3"
#     if id.find("ns", 0) <> -1:
#         id2 = id2 + "4"
#     if id.find("mx", 0) <> -1:
#         id2 = id2 + "5"
#     if id.find("soa", 0) <> -1:
#         id2 = id2 + "6"
#     if id.find("txt", 0) <> -1:
#         id2 = id2 + "7"
#     if id.find("no demands", 0) <> -1:
#         id2 = id2 + "1"
#     if id2=="":
#         return "error2"
#     print id2
#
#     # 处理参数3
#     id3=""
#     id = parameter3.lower()
#     if id.find("header", 0) <> -1:
#         id3 = id3 + "2"
#     if id.find("answers", 0) <> -1:
#         id3 = id3 + "3"
#     if id.find("authority", 0) <> -1:
#         id3 = id3 + "4"
#     if id.find("additional", 0) <> -1:
#         id3 = id3 + "5"
#     if id.find("querytime", 0) <> -1:
#         id3 = id3 + "6"
#     if id.find("no demands", 0) <> -1:
#         id3 = id3 + "1"
#     if id3=="":
#         return "error3"
#     print id3
#
#     dns=""
#     appoint=""
#     #get dns
#     if id1=="1":
#         fenge=parameter1.find(":",0)
#         dns=parameter1[fenge+1:]
#     if id1=="2":
#         fenge=parameter1.find(":",0)
#         appoint=parameter1[fenge+1:]
#
#     instance2=MyTest2(id1,id2,id3,dns,appoint)
#     result=instance2.output()
#     return jsonify(result)
#     #return 'You are reading '+u'可看到！ ' + id2



if __name__ == "__main__":
    #db1 = mysql_connect.connect('FengYJ_DNS')
    #db2 = mysql_connect.connect('FengYJ_dnstool')
    mpid = os.getpid()
    main_process_group_id = os.getpgid(mpid)

    with open('./gid.txt', 'w') as f:
        f.write(str(main_process_group_id))
    APP.config['JSON_AS_ASCII'] = False
    APP.run(host='0.0.0.0', debug=False,threaded=True,port=7777)
    #mysql_connect.close_connect(db1, cursor1)
    #mysql_connect.close_connect(db2, cursor2)
#http://127.0.0.1:7777/test


