# -*- coding: UTF-8 -*-

'''
封装类
'''
import MySQLdb
#import pymysql
#pymysql.install_as_MySQLdb()
import DNS
import os
import threading
import inspect
import ctypes
import ipaddress
import copy
import socket
import info


def byteify(input, encoding='utf-8'):
    if isinstance(input, dict):
        return {byteify(key): byteify(value) for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode(encoding)
    else:
        return input


def getQtypeAnswers(name, type, server, protocol='udp', times=1):
    success = 0
    try:
        r = DNS.DnsRequest(name=name, qtype=type, server=server, protocol=protocol, timeout=1)
        answerslist = r.req()
        # while answerslist.header['ancount'] == 0 :
        # times = times + 1
    # answerslist = getQtypeAnswers(name,type,server,protocol,times)
        return answerslist
    except:
        # print "Timeout",name,type,server
        # logging.error(("Timeout 5 times",name,type,server))
        return 0


def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


class myThread2(threading.Thread):

    def __init__(self, mytest3, dns, lock, num):
        threading.Thread.__init__(self)
        #self.threadID = threadID
        #self.name = name
        self.mytest3 = mytest3
        self.dns = dns
        # self.country = country
        # self.prov = prov
        # self.city = city
        # self.isp = isp
        #self.typename = typename
        self.lock = lock
        self.num = num
        #self.counter = counter

    def run(self):
        with self.num:
            self.lock.acquire()
            self.answerlist, self.result_dict, self.unique = Batch.resolve_dns(self.mytest3, self.dns)
            #print_time(self.name, self.counter, 3)
            # 释放锁
            self.lock.release()

    def get_result(self):
        try:
            return self.answerlist, self.result_dict, self.unique  # 如果子线程不使用join方法，此处可能会报没有self.result的错误
        except Exception:
            return None

    def _get_my_tid(self):
        """determines this (self's) thread id"""
        if not self.isAlive():
            raise threading.ThreadError("the thread is not active")
        # do we have it cached?
        if hasattr(self, "_thread_id"):
            return self._thread_id
        # no, look for it in the _active dict
        for tid, tobj in threading._active.items():
            if tobj is self:
                self._thread_id = tid
                return tid
        raise AssertionError("could not determine the thread's id")

    def raise_exc(self, exctype):
        """raises the given exception type in the context of this thread"""
        _async_raise(self._get_my_tid(), exctype)

    def terminate(self):
        """raises SystemExit in the context of the given thread, which should
        cause the thread to exit silently (unless caught)"""
        self.raise_exc(SystemExit)

class myThread3(threading.Thread):

    def __init__(self, mytest3, region, lock, num):
        threading.Thread.__init__(self)
        #self.threadID = threadID
        #self.name = name
        self.mytest3 = mytest3
        self.region = region
        #self.typename = typename
        self.lock = lock
        self.num = num
        #self.counter = counter

    def run(self):
        with self.num:
            self.lock.acquire()
            self.over = Batch.traverse_each_city_isp1(self.mytest3, self.region)
            #print_time(self.name, self.counter, 3)
            # 释放锁
            self.lock.release()

    def _get_my_tid(self):
        """determines this (self's) thread id"""
        if not self.isAlive():
            raise threading.ThreadError("the thread is not active")
        # do we have it cached?
        if hasattr(self, "_thread_id"):
            return self._thread_id
        # no, look for it in the _active dict
        for tid, tobj in threading._active.items():
            if tobj is self:
                self._thread_id = tid
                return tid
        raise AssertionError("could not determine the thread's id")

    def get_result(self):
        try:
            return self.over  # 如果子线程不使用join方法，此处可能会报没有self.result的错误
        except Exception:
            return None

    def raise_exc(self, exctype):
        """raises the given exception type in the context of this thread"""
        _async_raise(self._get_my_tid(), exctype)

    def terminate(self):
        """raises SystemExit in the context of the given thread, which should
        cause the thread to exit silently (unless caught)"""
        self.raise_exc(SystemExit)

class myThread4(threading.Thread):

    def __init__(self, mytest3, region, lock, num):
        threading.Thread.__init__(self)
        #self.threadID = threadID
        #self.name = name
        self.mytest3 = mytest3
        self.region = region
        #self.typename = typename
        self.lock = lock
        self.num = num
        #self.counter = counter

    def run(self):
        with self.num:
            self.lock.acquire()
            self.over = Batch.traverse_each_city_isp2(self.mytest3, self.region)
            #print_time(self.name, self.counter, 3)
            # 释放锁
            self.lock.release()

    def get_result(self):
        try:
            return self.over  # 如果子线程不使用join方法，此处可能会报没有self.result的错误
        except Exception:
            return None

    def _get_my_tid(self):
        """determines this (self's) thread id"""
        if not self.isAlive():
            raise threading.ThreadError("the thread is not active")
        # do we have it cached?
        if hasattr(self, "_thread_id"):
            return self._thread_id
        # no, look for it in the _active dict
        for tid, tobj in threading._active.items():
            if tobj is self:
                self._thread_id = tid
                return tid
        raise AssertionError("could not determine the thread's id")

    def raise_exc(self, exctype):
        """raises the given exception type in the context of this thread"""
        _async_raise(self._get_my_tid(), exctype)

    def terminate(self):
        """raises SystemExit in the context of the given thread, which should
        cause the thread to exit silently (unless caught)"""
        self.raise_exc(SystemExit)

class Batch(object):
    def __init__(self, domain,typestr,vital_num):
        self.domainname = domain
        self.type = typestr
        self.vital_num = vital_num

        db_host_ip = os.environ['DNS_DB_IP']
        self.db1 = MySQLdb.connect(host=db_host_ip, charset='utf8', user='root', passwd='platform', db='domain_resolve')
        self.cursor1 = self.db1.cursor()
        self.db2 = MySQLdb.connect(host=db_host_ip, charset='utf8', user='root', passwd='platform', db='domain_resolve')
        self.cursor2 = self.db2.cursor()

        self.address_list = []
        self.a_address_list = []
        self.aaaa_address_list = []
        self.cname_address_list = []
        self.mx_address_list = []
        self.ns_address_list = []
        self.soa_address_list = []
        self.txt_address_list = []
        self.result_list = []
        #self.answer_list = []
        self.threads = []
        self.unique_dns_list = []
        self.bad_dns_list = []
        self.unique_list = []
        self.none_list =[]
        self.dns_list = []
        self.over = 0

        self.result = []
        self.result2 = {}

    def traverse_each_city_isp1(self, pinyin_region):#遍历各市、各运营商的DNS，发送解析请求
        lock = threading.Lock()
        num = threading.Semaphore(100)

        sql = "select ip,country,prov,city,isp from %s group by city,isp"%pinyin_region
        #print sql

        self.cursor1 = self.db1.cursor()
        self.cursor1.execute(sql)
        results = self.cursor1.fetchall()
        self.cursor1.close()
        for result in results:
            dns = str(result[0]).strip()
            country = str(result[1]).strip()
            prov = str(result[2]).strip()
            city = str(result[3]).strip()
            isp = str(result[4]).strip()
            #print '----------------------------'
            #print dns, country, prov, city, isp
            unique = 0
            if dns not in self.dns_list and dns not in self.bad_dns_list:#当前DNS未测过，且不在不响应DNS列表中
                self.dns_list.append(dns)
                #print server, dns_list
                t = myThread2(self, dns, lock, num)
                #t.setDaemon(False)
                self.threads.append(t)
                t.start()
                if t.isAlive():
                    t.join()

                answerslist, result_dict, unique = t.get_result()

                if result_dict:
                    result_dict['country'] = country
                    result_dict['province'] = prov
                    result_dict['city'] = city
                    result_dict['isp'] = isp

                    self.result_list.append(result_dict)
                    print '截止目前所有结果列表如下：'
                    print 'result_list',self.result_list

                if answerslist != 0:
                    #print 'answerslist.header'
                    #print answerslist.header
                    #print 'answerslist.answers'
                    #print answerslist.answers
                    if answerslist.header['ancount'] != 0:
                        if unique == 0:
                           # print 'unique 0'
                            comp_list = self.unique_list[0 - self.vital_num:]
                            #print comp_list
                            if 1 not in comp_list:
                                #print 'loop over!!!!!!!!!!!!!!!!'
                                #print self.threads
                                for t in self.threads:
                                    #print t
                                    if t.isAlive():
                                        #print 'stop', t
                                        t.terminate()
                                self.over = 1
                                #print 'return 1'
                                return 1
                    else:
                        if answerslist.header['nscount'] != 0 or answerslist.header['arcount'] != 0:
                            self.none_list.append(0)
                            if len(self.none_list) > 3 and 1 not in self.none_list:
                                print '出现请求类型不适合：'
                                print 'self.none_list', self.none_list
                                #print 'loop over'
                                for t in self.threads:
                                    #print t
                                    if t.isAlive():
                                        #print 'stop', t
                                        t.terminate()
                                self.over = 1
                                return 1
                else:
                    self.bad_dns_list.append(dns)
                    sql= "select ip,country,prov,city,isp from %s where ODNS = 1 and abnormal != 1 and city like '%s' and isp like '%s' " \
                         "order by latest_find_time desc,find_times desc limit 50"\
                            %(pinyin_region, city+'%', isp+'%')
                    #print sql

                    self.cursor1 = self.db1.cursor()
                    self.cursor1.execute(sql)
                    sub_results = self.cursor1.fetchall()
                    self.cursor1.close()
                    for result in sub_results:
                        sub_dns = str(result[0]).strip()
                        country = str(result[1]).strip()
                        prov = str(result[2]).strip()
                        city = str(result[3]).strip()
                        isp = str(result[4]).strip()
                        if sub_dns not in self.dns_list and dns not in self.bad_dns_list:#当前DNS未测过，且不在不响应DNS列表中
                            self.dns_list.append(sub_dns)
                            t = myThread2(self, sub_dns, lock, num)
                            #t.setDaemon(False)
                            self.threads.append(t)
                            t.start()
                            if t.isAlive():
                                t.join()

                            answerslist, result_dict, unique = t.get_result()

                            if result_dict:
                                result_dict['country'] = country
                                result_dict['province'] = prov
                                result_dict['city'] = city
                                result_dict['isp'] = isp

                                self.result_list.append(result_dict)
                                print '截止目前所有结果列表如下：'
                                print 'result_list', self.result_list

                            if answerslist != 0:
                                #print answerslist.header
                                #print answerslist.answers
                                if answerslist.header['ancount'] != 0:
                                    if unique == 0:
                                        #print 'unique 0'
                                        comp_list = self.unique_list[0 - self.vital_num:]
                                        #print comp_list
                                        if 1 not in comp_list:
                                            #print 'loop over~~~~~~~~~~~~'
                                            for t in self.threads:
                                                #print t
                                                if t.isAlive():
                                                    #print 'stop', t
                                                    t.terminate()
                                            self.over = 1
                                            return 1
                                    #break
                                else:
                                    if answerslist.header['nscount'] != 0 or answerslist.header['arcount'] != 0:
                                        self.none_list.append(0)
                                        if len(self.none_list) > 3 and 1 not in self.none_list:
                                            print '出现请求类型不适合：'
                                            print 'self.none_list', self.none_list
                                            # print 'loop over'
                                            for t in self.threads:
                                                # print t
                                                if t.isAlive():
                                                    # print 'stop', t
                                                    t.terminate()
                                            self.over = 1
                                            return 1
                            else:
                                self.bad_dns_list.append(dns)
        return 2

    def traverse_each_city_isp2(self, pinyin_region):#向其他DNS请求
        #threads = []
        lock = threading.Lock()
        num = threading.Semaphore(100)
        unique = 0
        sql = "select ip,country,prov,city,isp from %s where ODNS = 1 and abnormal != 1 " \
              "order by latest_find_time desc,find_times desc limit 50"%pinyin_region
        #print sql

        self.cursor1 = self.db1.cursor()
        self.cursor1.execute(sql)
        results = self.cursor1.fetchall()
        self.cursor1.close()
        for result in results:
            dns = str(result[0]).strip()
            country = str(result[1]).strip()
            prov = str(result[2]).strip()
            city = str(result[3]).strip()
            isp = str(result[4]).strip()
            if dns not in self.dns_list and dns not in self.bad_dns_list:
                self.dns_list.append(dns)
                #print server, dns_list
                t = myThread2(self, dns, lock, num)
                #t.setDaemon(True)
                self.threads.append(t)
                t.start()
                if t.isAlive():
                    t.join()

                answerslist, result_dict, unique = t.get_result()

                if result_dict:
                    result_dict['country'] = country
                    result_dict['province'] = prov
                    result_dict['city'] = city
                    result_dict['isp'] = isp

                    self.result_list.append(result_dict)
                    print '截止目前所有结果列表如下：'
                    print 'result_list', self.result_list

                if answerslist != 0:
                    if answerslist.header['ancount'] != 0:
                        if unique == 0:  # 不是返回新增地址的DNS，跳过该region其他DNS
                            #print 'unique 0'
                            comp_list = self.unique_list[0 - self.vital_num:]
                            #print comp_list
                            if 1 not in comp_list:
                                #print 'loop over。。。。。。。。。。。'
                                # 返回已有地址的DNS比返回新增地址的DNS多，且连续100个DNS返回已有地址, 跳出循环
                                for t in self.threads:
                                    # print t
                                    if t.isAlive():
                                        # print 'stop', t
                                        t.terminate()
                                self.over = 1
                                return 1
                    else:
                        if answerslist.header['nscount'] != 0 or answerslist.header['arcount'] != 0:
                            self.none_list.append(0)
                            if len(self.none_list) > 3 and 1 not in self.none_list:
                                print '出现请求类型不适合：'
                                print 'self.none_list', self.none_list
                                #print 'loop over'
                                for t in self.threads:
                                    #print t
                                    if t.isAlive():
                                        #print 'stop', t
                                        t.terminate()
                                self.over = 1
                                return 1
                else:
                    self.bad_dns_list.append(dns)
        return 2

    def is_ipv6(ip):
        try:
            socket.inet_pton(socket.AF_INET6, ip)
        except socket.error:  # not a valid ip
            return False
        return True


    def resolve_dns(self, dns):#域名解析核心
        queryname = self.domainname

        if self.type == 'A':
            typename = DNS.Type.A
        elif self.type == 'AAAA':
            typename = DNS.Type.AAAA
        elif self.type == 'CNAME':
            typename = DNS.Type.CNAME
        elif self.type  == 'MX':
            typename = DNS.Type.MX
        elif self.type  == 'NS':
            typename = DNS.Type.NS
        elif self.type  == 'PTR':
            typename = DNS.Type.PTR
            ip_char_list = queryname.split('.')
            queryname = ip_char_list[3] + '.' + ip_char_list[2] + '.' + ip_char_list[1] + '.' + ip_char_list[0] + '.in-addr.arpa'
        elif self.type  == 'SOA':
            typename = DNS.Type.SOA
        elif self.type == 'TXT':
            typename = DNS.Type.TXT

        unique = 0
        strange_list = ['!', '\"', '#', '$', '%', '&', '\\', '\'', '(', ')', '*', '+', ',', '/', ':', ';', '?', '@',
                        '[', '\]', '^', '_', '{', '|', '}', '~']

        dns_address_list = []
        dns_answer_list = []
        diff_address_list = []
        result_dict = {}
        answerslist = getQtypeAnswers(queryname , typename, dns)
        # print answerslist
        if answerslist != 0:
            if answerslist.header['ancount'] != 0:
                for item in answerslist.answers:
                    address = item['data']
                    try:
                        for char in strange_list:
                            if str(address).find(char) != -1:#IPv6地址
                                address = ipaddress.ip_address(address)
                    except:
                        pass

                    address = str(address).lower()#全部转成小写
                    dns_address_list.append(address)
                    answer = {'name': str(item['name']), 'ttl': str(item['ttl']), 'typename': str(item['typename']),
                              'data': address}
                    dns_answer_list.append(answer)
                #print dns_answer_list
                dns_answer_list.sort()
                #print '-----------------'
                #print dns
                #print dns_answer_list
                #print '-----------------'

                diff_address_list = list(set(dns_address_list).difference(set(self.address_list)))#当前DNS解析结果与已有解析结果做差集

                #print '当前DNS解析出结果如下：'
                #print 'dns_address_list', dns_address_list
                #print '已有DNS解析结果如下：'
                #print 'self.address_list', self.address_list
                #print '差集如下：'
                #print 'diff_address_list', diff_address_list

                if diff_address_list:#当前DNS解析出新的结果，则写入地址列表，结果字典
                    #print diff_address_list
                    #print 'add address'
                    self.address_list = self.address_list + diff_address_list
                    result_dict = {'dns': dns, 'answer list': dns_answer_list, 'query time': str(round(answerslist.args['elapsed'],2))+'ms'}
                    #self.result_list.append(result_dict)
                    #print '新增结果字典如下：'
                    #print result_dict
                    #print self.result_list
                    unique = 1

                if unique == 1:#当前DNS优秀
                    self.unique_dns_list.append(dns)
                    #print 'line141', self.unique_dns_list

                self.unique_list.append(unique)
                #print 'unique',unique
                #print '截至目前有响应DNS的解析结果唯一性列表如下：'
                #print 'unique_list',self.unique_list
                #print '--------------'
                #print 'line149', self.unique_dns_list
                #continue
        else:
            self.bad_dns_list.append(dns)
        return answerslist, result_dict, unique

    def read_region(self):#读取省份文件
        region_dict = []
        current_path = os.path.abspath(__file__)
        father_path = os.path.abspath(os.path.dirname(current_path) + os.path.sep + ".")

        f_region = open(father_path + '/region.txt', 'r')
        while True:
            str_line = f_region.readline()
            if str_line:
                str_line = str_line.strip()
                cn_region = str_line.split(' ')[0]
                pinyin_region = str_line.split(' ')[1]
                region_dict.append(pinyin_region + "," + cn_region)
                # print region_dict[cn_region]
            else:
                break
        f_region.close()
        return region_dict

    def thread_resolve_nothas1(self, region_dict):
        #print 'has1'
        threads = []
        lock = threading.Lock()
        num = threading.Semaphore(100)

        dns_list = []
        unique_list = []
        unique = 0

        for one_region in region_dict:
            pinyin_region = str(one_region.split(",")[0])
            #print pinyin_region
            t = myThread3(self, pinyin_region, lock, num)
            t.setDaemon(True)
            # t.start()
            # time.sleep(0.1)
            threads.append(t)
        for t in threads:
            t.start()
        for t in threads:
            #print 'i am', t
            if t.isAlive():
                t.join()
            if t.get_result() == 1:
                #print 'has return 11111111111'
                for t1 in threads:
                    #print t1
                    if t1.isAlive():
                        #print 'stop'
                        t1.terminate()
                return 1
            else:
                t.join()
        return 2
        #t.join()

    def thread_resolve_nothas2(self, region_dict):
        #print 'has2'
        threads = []
        lock = threading.Lock()
        num = threading.Semaphore(100)

        dns_list = []
        unique_list = []
        unique = 0

        for one_region in region_dict:
            pinyin_region = str(one_region.split(",")[0])
            #print pinyin_region
            t = myThread4(self, pinyin_region, lock, num)
            t.setDaemon(True)
            # t.start()
            # time.sleep(0.1)
            threads.append(t)
        for t in threads:
            t.start()
        for t in threads:
            #print 'i am', t
            if t.isAlive():
                t.join()
            if t.get_result() == 1:
                #print '11111111'
                for t1 in threads:
                    if t1.isAlive():
                        #print 'stop'
                        t1.terminate()
                return 1
            else:
                t.join()
        return 2

    def find_dns_info(self, dns, good_dns_dict_list):#从优秀DNS信息字典中读取信息
        for good_dns_dict in good_dns_dict_list:
            good_dns = good_dns_dict.get('dns')
            if good_dns == dns:
                country = good_dns_dict.get('country')
                prov = good_dns_dict.get('province')
                city = good_dns_dict.get('city')
                isp = good_dns_dict.get('isp')
                return country, prov, city, isp
        return '','','',''


    def traverse_good_dns(self, good_dns_list, good_dns_dict_list):#向优秀DNS逐个请求域名解析
        #threads = []
        lock = threading.Lock()
        num = threading.Semaphore(100)
        unique = 0
        for dns in good_dns_list:
            if dns not in self.dns_list and dns not in self.bad_dns_list:
                self.dns_list.append(dns)
                # print server, dns_list
                t = myThread2(self, dns, lock, num)#发送域名解析请求
                # t.setDaemon(True)
                self.threads.append(t)
                t.start()
                if t.isAlive():
                    t.join()

                answerslist, result_dict, unique = t.get_result()#获取解析结果

                country, prov, city, isp = self.find_dns_info(dns, good_dns_dict_list)

                if result_dict:
                    result_dict['country'] = country
                    result_dict['province'] = prov
                    result_dict['city'] = city
                    result_dict['isp'] = isp

                    #print dns,country, prov, city, isp
                    #print result_dict
                    self.result_list.append(result_dict)
                    #print '截止目前所有结果列表如下：'
                    #print 'result_list',self.result_list

                if answerslist != 0:
                    if answerslist.header['ancount'] != 0:
                        if unique == 0: # 不是返回新增地址的DNS
                            # print 'unique 0'
                            comp_list = self.unique_list[0 - self.vital_num:]
                            # print comp_list
                            if 1 not in comp_list:#连续vital_num个DNS返回已有地址, 跳出循环
                                #print 'loop over``````````````````'
                                for t in self.threads:
                                    # print t
                                    if t.isAlive():
                                        # print 'stop', t
                                        t.terminate()
                                self.over = 1
                                return 1
                    else:
                        if answerslist.header['nscount'] != 0 or answerslist.header['arcount'] != 0:
                            self.none_list.append(0)
                            if len(self.none_list) > 3 and 1 not in self.none_list:#三个以上响应包均为没有answer部分，则该类型请求本身无响应，退出
                                # print 'loop over'
                                for t in self.threads:
                                    # print t
                                    if t.isAlive():
                                        # print 'stop', t
                                        t.terminate()
                                self.over = 1
                                return 1
                else:
                    self.bad_dns_list.append(dns)#解析无响应的DNS
        return 0


    def update_single_dns(self, dns, country, prov, city, isp, quality):#对单个DNS插入数据
        sql = "select * from past_dns where dns = '%s' and type = '%s'" % (dns,self.type)
        self.cursor2 = self.db2.cursor()
        self.cursor2.execute(sql)
        result = self.cursor2.fetchone()
        # cursor2 = self.db2.cursor()
        self.cursor2.close()
        #self.cursor2 = self.db2.cursor()
        now_domain_str = ''
        domain_num = 0
        if result:#库中有该DNS
            past_country = str(result[1])
            past_prov = str(result[2])
            past_city = str(result[3])
            past_isp = str(result[4])
            past_domain_str = str(result[6])
            past_domain_num = int(result[7])
            past_quality = str(result[8])
            if past_quality == 'good':
                past_domain_list = past_domain_str.split(',')
                if quality == 'good':#以前和现在都good
                    if self.domainname not in past_domain_list:#以前没有该域名，则插入域名、更改域名数量
                        past_domain_list.append(self.domainname)
                        now_domain_str = ','.join(past_domain_list)
                        domain_num = past_domain_num + 1
                    else:#以前有该域名，则保持不变
                        now_domain_str = ','.join(past_domain_list)
                        domain_num = past_domain_num
                else:#以前good，现在非good
                    if self.domainname in past_domain_list:#以前有该域名，则删除该域名
                        past_domain_list.remove(self.domainname)
                        now_domain_str = ','.join(past_domain_list)
                        domain_num = past_domain_num - 1
                        if domain_num >= 1:
                            quality = 'good'
                    else:#以前没有该域名，则保持不变
                        now_domain_str = ','.join(past_domain_list)
                        domain_num = past_domain_num
                        quality = 'good'
            else:
                if quality == 'good':#以前非good，现在good，则更改内容
                    now_domain_str = self.domainname
                    domain_num = 1
                else:#以前和现在都非good，则保持不变
                    pass
            if past_country and past_prov and past_city and past_isp:
                pass
            else:
                if country and prov and city and isp:
                    sub_sql1 = "update past_dns set country = '%s' where dns = '%s'" % (country, dns)
                    self.cursor2 = self.db2.cursor()
                    self.cursor2.execute(sub_sql1)
                    sub_sql2 = "update past_dns set prov = '%s' where dns = '%s'" % (prov, dns)
                    self.cursor2 = self.db2.cursor()
                    self.cursor2.execute(sub_sql2)
                    sub_sql3 = "update past_dns set city = '%s' where dns = '%s'" % (city, dns)
                    self.cursor2 = self.db2.cursor()
                    self.cursor2.execute(sub_sql3)
                    sub_sql4 = "update past_dns set isp = '%s' where dns = '%s'" % (isp, dns)
                    self.cursor2 = self.db2.cursor()
                    self.cursor2.execute(sub_sql4)
            sub_sql5 = "update past_dns set domain_list = '%s' where dns = '%s' and type = '%s'" % (now_domain_str, dns, self.type)
            self.cursor2 = self.db2.cursor()
            self.cursor2.execute(sub_sql5)
            sub_sql6 = "update past_dns set domain_num = '%s' where dns = '%s' and type = '%s'" % (domain_num, dns, self.type)
            self.cursor2 = self.db2.cursor()
            self.cursor2.execute(sub_sql6)
            sub_sql7 = "update past_dns set quality = '%s' where dns = '%s' and type = '%s'" % (quality, dns, self.type)
            self.cursor2 = self.db2.cursor()
            self.cursor2.execute(sub_sql7)
        else:#库中无该type的DNS
            sql = "select * from past_dns where dns = '%s'" % (dns)
            self.cursor2 = self.db2.cursor()
            self.cursor2.execute(sql)
            results = self.cursor2.fetchall()
            self.cursor2.close()
            for result in results:
                past_country = str(result[1])
                past_prov = str(result[2])
                past_city = str(result[3])
                past_isp = str(result[4])
                if past_country and past_prov and past_city and past_isp:
                    country = past_country
                    prov= past_prov
                    city = past_city
                    isp = past_isp
                    break
            if quality == 'good':
                now_domain_str = self.domainname
                domain_num = 1
            else:
                pass
            sub_sql = "insert into past_dns(dns,country,prov,city,isp,type,domain_list,domain_num,quality) " \
                      "values('%s','%s','%s','%s','%s','%s','%s',%d,'%s')" \
                      % (dns,country,prov,city,isp,self.type,now_domain_str,domain_num,quality)
            #print sub_sql
            self.cursor2 = self.db2.cursor()
            self.cursor2.execute(sub_sql)
        self.db2.commit()
        self.cursor2.close()

    def update_past_dns(self):#更新DNS属性表
        common_dns_list = list(set(self.dns_list).difference(set(self.unique_dns_list)))
        common_dns_list = list(set(common_dns_list).difference(set(self.bad_dns_list)))#找到普通DNS
        for result_dict in self.result_list:#结果字典中DNS均为优秀
            #print result_dict
            dns = result_dict.get('dns')
            country = result_dict.get('country')
            prov = result_dict.get('province')
            city = result_dict.get('city')
            isp = result_dict.get('isp')
            #print dns, country, prov, city, isp
            if country and prov and city and isp:
                pass
            else:
                country, prov, city, isp = info.find_info(dns)
                result_dict['country'] = country
                result_dict['province'] = prov
                result_dict['city'] = city
                result_dict['isp'] = isp
            quality = 'good'
            #print 'good DNS：'
            #print dns, country, prov, city, isp, quality
            self.update_single_dns(dns, country, prov, city, isp, quality)
        for dns in common_dns_list:
            country = ''
            prov = ''
            city = ''
            isp = ''
            quality = 'common'
            #print 'common DNS：'
            #print dns, country, prov, city, isp, quality
            self.update_single_dns(dns, country, prov, city, isp, quality)
        #for dns in self.bad_dns_list:
            #quality = 'bad'
            #print 'bad DNS：'
            #print dns, country, prov, city, isp, quality
            #self.update_single_dns(dns, country, prov, city, isp, quality)


    def update_resolve_history(self):#更新解析结果表
        for result_dict in self.result_list:#从结果列表中读取每个结果字典
            dns = result_dict.get('dns')
            dns_answer_list = result_dict.get('answer list')
            dns_answer_list_copy = copy.deepcopy(dns_answer_list)
            for answer_dict in dns_answer_list_copy:
                answer_dict.pop('ttl')#去掉TTL后和库中数据比较
            #print dns_answer_list_copy
            dns_answer_list_copy.sort()
            #print dns_answer_list_copy,type(dns_answer_list_copy)
            dns_answer_list_str = ','.join('%s' % id for id in dns_answer_list_copy)
            dns_answer_list_str = dns_answer_list_str.replace("\"","")
            #print 'now-------------',self.result_list
            #print dns_answer_list_str
            query_time = result_dict.get('query time')

            sql = "select * from resolve_history where domain = '%s' and type = '%s' and dns = '%s' and answer_list = \"%s\" order by time desc" \
                  % (self.domainname, self.type, dns, dns_answer_list_str)
            #print sql
            self.cursor2 = self.db2.cursor()
            self.cursor2.execute(sql)
            result = self.cursor2.fetchone()
            self.cursor2.close()

            if result:#库中存在相同域名、类型、DNS、解析结果的数据
                sub_sql = "update resolve_history set time = CURRENT_TIMESTAMP() where domain = '%s' and type = '%s' and dns = '%s' and answer_list = \"%s\"" \
                          % (self.domainname, self.type, dns, dns_answer_list_str)
                #print sub_sql
                self.cursor2 = self.db2.cursor()
                self.cursor2.execute(sub_sql)
                sub_sql = "update resolve_history set query_time = '%s' where domain = '%s' and type = '%s' and dns = '%s' and answer_list = \"%s\"" \
                          % (query_time, self.domainname, self.type, dns, dns_answer_list_str)
                #print sub_sql
                self.cursor2 = self.db2.cursor()
                self.cursor2.execute(sub_sql)
            else:
                sub_sql = "insert into resolve_history(domain, type, dns, answer_list, query_time) values('%s', '%s', '%s', \"%s\", '%s')" % (
                    self.domainname, self.type, dns, dns_answer_list_str, query_time)
                #print sub_sql

                self.cursor2 = self.db2.cursor()
                self.cursor2.execute(sub_sql)
            self.db2.commit()
            self.cursor2.close()
        #cursor2.close()



    def find_bad_dns(self):#从past_dns表中读取无响应的DNS
        #now = datetime.datetime.now()
        bad_dns_list = []
        sql = "select dns from past_dns where quality = 'bad' order by time desc, domain_num desc"
        #print sql

        self.cursor2 = self.db2.cursor()
        self.cursor2.execute(sql)
        results = self.cursor2.fetchall()
        self.cursor2.close()
        #cursor2.close()
        if results:
            for result in results:
                dns = str(result[0])
                bad_dns_list.append(dns)
        return bad_dns_list

    def find_good_dns(self):#从past_dns表中读取优秀的DNS及其信息
        #now = datetime.datetime.now()
        has_dns_list = []
        good_dns_list = []
        good_dns_dict = {}
        good_dns_dict_list = []
        sql = "select * from past_dns order by quality desc, time desc, domain_num desc"
        #print sql

        self.cursor2 = self.db2.cursor()
        #cursor2 = self.db2.cursor()
        self.cursor2.execute(sql)
        results = self.cursor2.fetchall()
        self.cursor2.close()
        #cursor2.close()
        if results:
            for result in results:
                dns = str(result[0]).strip()
                country = str(result[1]).strip()
                prov = str(result[2]).strip()
                city = str(result[3]).strip()
                isp = str(result[4]).strip()
                domain_list = str(result[5]).split(',')
                if self.domainname in domain_list:
                    has_dns_list.append(dns)
                else:
                    good_dns_list.append(dns)
                if country and prov and city and isp:
                    good_dns_dict = {'dns':dns,'country':country,'province':prov,'city':city,'isp':isp}
                    #print '库中已有：'
                    #print dns, country, prov, city, isp
                    good_dns_dict_list.append(good_dns_dict)
        new_dns_list = has_dns_list + good_dns_list#把解析过该域名的DNS放在前面
        #print new_dns_list
        #print '数据中已有优秀DNS如下：'
        #print new_dns_list
        #print '这些DNS的信息如下：'
        #print good_dns_dict_list
        return new_dns_list,good_dns_dict_list

    def find_has_dns(self):
        dns_list = []
        sql = "select dns from domain_resolve where domain = '%s' order by time desc" % (self.domainname)
        print sql

        self.cursor2 = self.db2.cursor()
        #cursor2 = self.db2.cursor()
        self.cursor2.execute(sql)
        result = self.cursor2.fetchone()
        self.cursor2.close()
        #cursor2.close()
        if result:
            dns_list = str(result[0]).split(',')
        return dns_list

    def output(self):
        print '-------------------------------------------'
        print self.domainname,self.type,str(self.vital_num)

        good_dns_list, good_dns_dict_list = self.find_good_dns()#获取已有库中优秀DNS
        #self.bad_dns_list = self.find_bad_dns()
        #
        over = 0
        if good_dns_list:
            over = self.traverse_good_dns(good_dns_list,good_dns_dict_list)#向优秀DNS请求域名解析
        if over == 0:#优秀DNS请求完，但是结果未到预期
            region_dict = self.read_region()#读取各地区
            over1 = 0
            over2 = 0
            over1 = self.thread_resolve_nothas1(region_dict)#从DNS大库中遍历各市、各运营商DNS并请求
            if over1 == 2:#各市、各运营商DNS请求完，但是结果未到预期
                self.thread_resolve_nothas2(region_dict)#从DNS大库中读取其他DNS并请求

        self.unique_dns_list.sort()
        self.address_list.sort()
        #print 'dns_list', self.dns_list
        #print 'now_dns_list', self.unique_dns_list

        self.update_resolve_history()#更新解析结果表
        self.update_past_dns()#更新DNS属性表

        #print self.address_list

        results = {}
        #print '结果列表如下：'
        #print self.result_list
        self.result_list.sort()
        results[self.type] = self.result_list

        self.db1.close()
        self.db2.close()
        print '-------------------------------------------'
        return byteify(results)
