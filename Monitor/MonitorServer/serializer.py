#_*_coding:utf-8_*_
__author__ = 'Alex Li'

from MonitorServer import models
import json,time
from django.core.exceptions import  ObjectDoesNotExist

class ClientHandler(object):

    def __init__(self, client_id):
        self.client_id = client_id
        self.client_configs = {
            "services":{}
        }

    def fetch_configs(self):
        try:
            #通过id获取主机对象
            host_obj = models.Host.objects.get(id=self.client_id)
            #1）获取主机对象关联的模板
            template_list= list(host_obj.templates.select_related())
            #2）获取主机组，并获取主机组关联的模板
            for host_group in host_obj.host_groups.select_related():
                template_list.extend( host_group.templates.select_related() )
            #循环所有模板
            for template in template_list:
                #循环所有模板中的服务
                for service in template.services.select_related():
                    #生成配置文件
                    self.client_configs['services'][service.name] = [service.plugin_name,service.interval]

        except ObjectDoesNotExist:
            pass
        print(self.client_configs)
        return  self.client_configs

