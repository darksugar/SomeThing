from django.shortcuts import render,HttpResponse
from django.views import View
import json
from MonitorServer.serializer import ClientHandler
# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from MonitorServer.backends import data_optimization
from MonitorServer.backends import redis_conn
from django.conf import settings


REDIS_OBJ = redis_conn.redis_conn(settings)

class Client_config(View):

    def get(self, request, *args, **kwargs):
        print(args)
        client_id = args[0]
        config_obj = ClientHandler(client_id)
        config = config_obj.fetch_configs()

        if config:
            return HttpResponse(json.dumps(config))

class Client_report(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(Client_report, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        print("client data:", request.POST)
        # REDIS_OBJ.set("test_alex",'hahaha')
        try:
            print('host=%s, service=%s' % (request.POST.get('client_id'), request.POST.get('service_name')))
            data = json.loads(request.POST['data'])
            # print(data)
            # StatusData_1_memory_latest
            client_id = request.POST.get('client_id')
            service_name = request.POST.get('service_name')
            # 把数据存下来
            data_saveing_obj = data_optimization.DataStore(client_id, service_name, data, REDIS_OBJ)

            # redis_key_format = "StatusData_%s_%s_latest" %(client_id,service_name)
            # data['report_time'] = time.time()
            # REDIS_OBJ.lpush(redis_key_format,json.dumps(data))

        except IndexError as e:
            print('----->err:', e)

        return HttpResponse(json.dumps("---report success---"))