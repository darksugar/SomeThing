from django.shortcuts import render,HttpResponse
from .data_handler import DataProcess
from Analysis.backends import redis_conn,ip_lookup
from django.conf import settings
# Create your views here.

#生成REDIS_OBJ
REDIS_OBJ = redis_conn.redis_conn(settings)
#IP模拟数据
IP_DB_DATA = ip_lookup.IPLookup(ip_db_filename=settings.IP_DB_FILE).ip_db_data
# 如果前端页面打开了实时监测,所有指定区域来的数据到放到相应的Queue里
GLOBAL_REALTIME_WATCHING_QUEUES = {}


def data_report(request):

    data_process_obj = DataProcess(request,REDIS_OBJ,GLOBAL_REALTIME_WATCHING_QUEUES,IP_DB_DATA)
    if data_process_obj.is_valid():
        data_process_obj.save()
    else:
        print("invalid data:")

    msg = 'jsonpcallback({"Email":"alex@126.com","Remark":"我来自服务器端哈哈"})'
    return  HttpResponse(msg)