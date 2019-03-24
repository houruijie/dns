#! coding:utf-8

"""
    异步DNS类
"""
import time
import select
import random
import socket
import collections
from DNS import Lib
from DNS import Type
from DNS import Class
from DNS import Opcode


class AsyncRequest(object):
    """
        异步DNS请求
    """

    def __init__(self, sock_recv_buffer_size=1024 * 1024 * 5):
        """
            默认socket的recv buffer为3MiB
        """
        self.sock_recv_buffer_size = sock_recv_buffer_size

        self.sock = socket.socket(
            family=socket.AF_INET, type=socket.SOCK_DGRAM)

        # 这个选项需要命令支持：sysctl -w net.core.rmem_max=10485760
        self.sock.setsockopt(
            socket.SOL_SOCKET, socket.SO_RCVBUF, self.sock_recv_buffer_size)

    def refresh_socket(self):
        """
            使用一个新的socket
        """
        self.sock = socket.socket(
            family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.sock.setsockopt(
            socket.SOL_SOCKET, socket.SO_RCVBUF, self.sock_recv_buffer_size)

    def _add_qheader(self, packer, recursive, tid):
        """
            生成DNS请求的头部,并添加到packer中
        """
        # 操作为查询
        opcode = Opcode.QUERY
        # 期望递归
        if recursive:
            rd = 1
        else:
            rd = 0
        packer.addHeader(tid, 0, opcode, 0, 0, rd, 0, 0, 0, 1, 0, 0, 0)

    def _make_packet(self, server, qtype=Type.A, recursive=True, qclass=Class.IN, port=53):
        """
            组装探测请求包
        """
        domainlist = ['www.wizeye.com.cn', server]
        domain_id = {
            'www.wizeye.com.cn': 11111,
            server: 55555
        }
        packetlsit = []

        for domain in domainlist:
            packer = Lib.Mpacker()
            tid = domain_id[domain]

            if domain.split('.')[0] == 'www':
                self._add_qheader(packer, recursive, tid)
                packer.addQuestion(domain, qtype, qclass)
                request_data = packer.getbuf()
                packetlsit.append(request_data)
            else:
                ip_tips = domain.split('.')
                qname = ip_tips[3] + '.' + ip_tips[2] + \
                        '.' + ip_tips[1] + '.' + ip_tips[0]
                qname += '.in-addr.arpa'
                self._add_qheader(packer, recursive, tid)
                packer.addQuestion(qname, Type.PTR, qclass)
                request_data = packer.getbuf()
                packetlsit.append(request_data)

        return packetlsit

    def send(self, server, port=53):
        """
            发送请求数据包，不返回任何响应
        """
        try:
            packetlsit = self._make_packet(server)
            for packet in packetlsit:
                self.sock.sendto(packet, (server, port))
        except Exception as err:
            print "[PYTHON-89vdcv]", err

    def recv(self, timeout=1):
        """
            返回一个生成器，用于迭代socket在timeout内接受到的响应包及地址
        """
        while True:
            rsocket, wsocket, errsocket = select.select(
                [self.sock], [], [], timeout)

            if len(rsocket) == 0:
                return
            try:
                (response_buffer, address) = self.sock.recvfrom(65535)
                u = Lib.Munpacker(response_buffer)
                r = Lib.DnsResult(u, {})
            except:
                continue

            yield (r, address[0])


class MakeResult(object):
    """
       整合DNS响应结果
    """

    def __init__(self):
        pass

    def _unpack(self, restuple):
        """
            提取qname，rcode，acode
        """
        response = restuple[0]
        server = restuple[1]
        header = response.header
        answers = response.answers
        tid = header['id']
        result = []

        # print 'tid:',tid
        id_domain = {
            11111: 'www.wizeye.com.cn',
            55555: server
        }
        qname = id_domain[tid]
        rcode = header['rcode']
        aa=header['aa']
        acode = 0

        if tid != 55555:

            if header['ancount'] != 0:
                for answer in answers:
                    if answer['typename'] == 'A':
                        acode = 1
                        data = answer['data']
                        result.append(data)
        else:

            if header['ancount'] != 0:
                for answer in answers:
                    if answer['typename'] == 'PTR':
                        acode = 1
                        data = answer['data']
                        result.append(data)
            else:
                pass

        if tid in id_domain.keys():
            # print server,id_domain[tid],rcode,acode,result
            return server, id_domain[tid], rcode, acode,aa, result
        else:
            return

    def init_result(self, server):
        """
            初始化odns响应字典，默认值为timeout,rcode=-1,acode=-1,aa=-1
            DNS=0,AuDNS=0,ODNS=0,RDNS=0
        """
        domainlist = ['www.wizeye.com.cn',server]
        state_dic = {}
        state_dic['date'] = time.strftime("%Y-%m-%d", time.localtime())

        for domain in domainlist:
            state_dic.setdefault(domain, {'rcode': -1, 'acode': -1,'aa':-1,'data': []})

        state_dic['DNS']=0
        state_dic['AuDNS']=0
        state_dic['ODNS']=0
        #state_dic['RDNS']=0

        return state_dic

    def update_result(self, state_result, restuple):
        """
            更新响应结果
        """
        try:
            server, qname, rcode, acode,aa, result = self._unpack(restuple)
            state_result[server][qname]['rcode'] = rcode
            state_result[server][qname]['acode'] = acode
            state_result[server][qname]['data'] = result
            state_result[server][qname]['aa']=aa

        except:
            print '[ERROR 001]:abnormal pakcet'
            print restuple

    def classfy_DNS(self,state_result):
        """
            IP分类
        """
        domain = 'www.wizeye.com.cn'
        for ip, result in state_result.items():
            # print ip, result,'-----------'

            if result[ip]['rcode'] != -1:
                # print 'DNS'
                state_result[ip]['DNS']=1
            if result[domain]['aa'] == 1:
                # print 'AuDNS'
                state_result[ip]['AuDNS']=1
                state_result[ip]['DNS'] = 1
            if result[domain]['acode'] == 1:
                # print 'ODNS'
                state_result[ip]['ODNS']=1
                state_result[ip]['DNS'] = 1

def judge_DNS(ip_list):
    """
        判断IP是否为DNS及DNS类型,
        程序保留了解析结果，如有需求可以直接返回所有结果
    """
    sender = AsyncRequest()
    analyzer = MakeResult()
    state_result = {}
    judge_result={}
    a, b = 0, 0
    start_time = time.time()

    for ip in ip_list:
        state_result[ip] = analyzer.init_result(ip)
        sender.send(ip)
        a += 2

    for res in sender.recv():
        b += 1
        # responseCallback(res[0])
        analyzer.update_result(state_result, res)

    analyzer.classfy_DNS(state_result)
    # print result
    end_time = time.time()
    elapse = end_time - start_time
    sender.refresh_socket()
    # print "send:%d,recv:%d,pkt_loss_rate:%f,elapse=%f" % (a, b, 1 - float(b) / a, elapse)
    for ip,result in state_result.items():
        DNS=result['DNS']
        AuDNS=result['AuDNS']
        ODNS=result['ODNS']
        #RDNS=result['RDNS']
        judge_result[ip]={'DNS':DNS,'AuDNS':AuDNS,'ODNS':ODNS}

    return judge_result

def test():
    """
        AsyncSender使用示例
    """

    def responseCallback(response):
        print 'questions:', response.questions
        print 'header:', response.header
        print 'answers:', response.answers

    sender = AsyncRequest()
    analyzer = MakeResult()
    state_result = {}
    ips = ['111.38.102.67', '8.8.8.8']

    a, b = 0, 0
    start_time = time.time()

    for ip in ips:
        state_result[ip] = analyzer.init_result(ip)
        sender.send(ip)
        a += 2

    for res in sender.recv():
        b += 1
        # responseCallback(res[0])
        analyzer.update_result(state_result, res)

    analyzer.classfy_DNS(state_result)
    # print result
    end_time = time.time()
    elapse = end_time - start_time
    sender.refresh_socket()
    print '==========================='
    # print state_result
    print "send:%d,recv:%d,pkt_loss_rate:%f,elapse=%f" % (a, b, 1 - float(b) / a, elapse)



if __name__ == "__main__":
    ip_list= ['111.38.102.67', '8.8.8.8']
    judge_result=judge_DNS(ip_list)
    # for ip,result in judge_result.items():
    #     print ip,result
    print judge_result