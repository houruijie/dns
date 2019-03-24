# -*- coding: UTF-8 -*-

'''
封装类
'''

import MySQLdb
import os


# class Info(object):
#     def __init__(self):
#         pass

def find_info(dns):
    country = '未知'
    prov = '未知'
    city = '未知'
    isp = '未知'
    db_host_ip = os.environ['DNS_DB_IP']
    dns_char_list = dns.split('.')
    subnet = dns_char_list[0] + '.' + dns_char_list[1] + '.' + dns_char_list[2] + '.0'
    db1 = MySQLdb.connect(host=db_host_ip, charset='utf8', user='root', passwd='platform', db='domain_resolve')
    cursor1 = db1.cursor()
    sql = "select country,region,city,isp from ip_country_area_region_city_isp_segment where ip = '%s'" % (
        subnet)
    #print sql
    cursor1.execute(sql)
    result = cursor1.fetchone()
    db1.close()
    if result:
        country = str(result[0]).strip()
        prov = str(result[1]).strip()
        city = str(result[2]).strip()
        isp = str(result[3]).strip()
    #print country, prov, city, isp
    return country, prov, city, isp