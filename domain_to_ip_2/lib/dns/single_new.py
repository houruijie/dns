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
import datetime
import copy
import socket


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

class Single(object):
    def __init__(self, domain, dns, typestr):
        self.domainname = domain
        self.dns = dns
        self.type = typestr
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

    def find_info(self):
        country = '未知'
        prov = '未知'
        city = '未知'
        isp = '未知'

        dns_char_list = self.dns.split('.')
        subnet = dns_char_list[0] + '.' + dns_char_list[1] + '.' + dns_char_list[2] + '.0'
        sql = "select country,region,city,isp from ip_country_area_region_city_isp_segment where ip = '%s'" % (subnet)
        self.cursor1.execute(sql)
        result = self.cursor1.fetchone()
        if result:
            country = str(result[0]).strip()
            prov = str(result[1]).strip()
            city = str(result[2]).strip()
            isp = str(result[3]).strip()
        return country,prov,city,isp


    def resolve_dns(self):#域名解析核心

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
        query_time = 0
        header_dict = {}
        answer_list = []
        authority_list = []
        additional_list = []
        diff_address_list = []
        result_dict = {}
        answerslist = getQtypeAnswers(queryname , typename, self.dns)
        # print answerslist
        if answerslist != 0:
            header_dict = answerslist.header
            query_time = answerslist.args['elapsed']
            if answerslist.header['ancount'] != 0:
                for item in answerslist.answers:
                    address = item['data']
                    try:
                        for char in strange_list:
                            if str(address).find(char) != -1:#IPv6地址
                                address = ipaddress.ip_address(address)
                    except:
                        pass

                    #address = str(address).lower()#全部转成小写
                    #dns_address_list.append(address)
                    answer = {'name': str(item['name']), 'ttl': str(item['ttl']), 'typename': str(item['typename']),
                              'data': address}
                    answer_list.append(answer)
                #print dns_answer_list
                #dns_answer_list.sort()
                print '-----------------'
                #print self.dns
                print answer_list
                print '-----------------'
            if answerslist.header['nscount'] != 0:
                for item in answerslist.authority:
                    address = item['data']
                    try:
                        for char in strange_list:
                            if str(address).find(char) != -1:  # IPv6地址
                                address = ipaddress.ip_address(address)
                    except:
                        pass

                    # address = str(address).lower()#全部转成小写
                    # dns_address_list.append(address)
                    authority = {'name': str(item['name']), 'ttl': str(item['ttl']), 'typename': str(item['typename']),
                              'data': address}
                    authority_list.append(authority)
                # print dns_answer_list
                # dns_answer_list.sort()
                print '-----------------'
                #print self.dns
                print authority_list
                print '-----------------'
            if answerslist.header['arcount'] != 0:
                for item in answerslist.additional:
                    address = item['data']
                    try:
                        for char in strange_list:
                            if str(address).find(char) != -1:  # IPv6地址
                                address = ipaddress.ip_address(address)
                    except:
                        pass

                    # address = str(address).lower()#全部转成小写
                    # dns_address_list.append(address)
                    additional = {'name': str(item['name']), 'ttl': str(item['ttl']),
                                 'typename': str(item['typename']),
                                 'data': address}
                    additional_list.append(additional)
                # print dns_answer_list
                # dns_answer_list.sort()
                print '-----------------'
                # print self.dns
                print additional_list
                print '-----------------'



        return query_time, header_dict, answer_list, authority_list, additional_list


    def output(self):
        print '-------------------------------------------'
        print self.domainname, self.dns, self.type

        query_time, header_dict, answer_list, authority_list, additional_list = self.resolve_dns()

        record_dict = { 'query time': str(round(query_time, 2)) + 'ms',
                        'header': header_dict,
                        'answer': answer_list,
                        'authority': authority_list,
                        'additional': additional_list
                       }

        result_dict = {}

        result_dict[self.type] = record_dict

        self.db1.close()
        self.db2.close()

        print '-------------------------------------------'
        return byteify(result_dict)
