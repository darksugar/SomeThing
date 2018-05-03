from django.shortcuts import render,HttpResponse,redirect
from django.conf import settings
from web import models
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,logout,login
from backend.task_manager import  MultiTaskManger
import os,re,json
# Create your views here.

def index(request):
    '''index'''
    return render(request,'index.html')

def acc_login(request):

    error_msg = ''

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username,password=password)
        if user:
            login(request,user)
            return redirect("/")
        else:
            error_msg = "Wrong username or password!"
    return render(request,"login.html",{'error_msg':error_msg})

def acc_logout(request):
    logout(request)
    return redirect("/login/")

@login_required
def webssh(request):
    messages.info(request,'Hey,My info messages!')
    messages.success(request,'Hey,My success messages!')
    messages.warning(request,'Hey,My warning messages!')


    return render(request,'web_ssh.html')

@login_required
def user_audit(request):
    '''审计日志页面'''
    #从配置文件读取日志目录并返回
    log_path = settings.LOG_PATH
    log_dirs = os.listdir(log_path)

    return render(request,'user_audit.html',{'log_dirs':log_dirs})

def user_audit_detail(request,log_date):
    '''审计日志详细页面'''

    log_path = settings.LOG_PATH
    log_path_detail = os.path.join(log_path,log_date)
    log_path_detail_list = os.listdir(log_path_detail)
    print(log_path_detail_list)
    session_id_list = []
    for file_name in log_path_detail_list:
        session_id_list.append(re.search('\d+',file_name).group())

    session_objs = models.Session.objects.filter(id__in=session_id_list).select_related()
    print(session_objs)
    return render(request,'user_audit_file_list.html',{'session_objs':session_objs,
                                                       'log_date':log_date})


def user_audit_log_detail(request,log_date,session_id):
    log_file = os.path.join(settings.LOG_PATH,log_date,"session_%s.log" % session_id)
    from backend import audit
    audit_handler = audit.AuditLogHandler(log_file)
    cmd_list = audit_handler.parse()

    return render(request,'user_audit_detail.html',{'cmd_list':cmd_list,})

@login_required
def multitask_cmd(request):
    '''批量命令主页'''
    return render(request, "multitask_cmd.html")

@login_required
def multitask_file_transfer(request):
    '''批量文件'''
    return render(request,'multitask_file_transfer.html')


@login_required
def multitask(request):
    '''批量任务提交'''
    print("--->",request.POST)
    task_data = json.loads(request.POST.get('task_data'))
    print("--->selcted hosts",task_data)

    task_obj= MultiTaskManger(request)
    selected_hosts = list(task_obj.task.tasklogdetail_set.all().values('id', 'bind_host__host__ip_addr',
                                                             'bind_host__host__hostname', 'bind_host__remote_user__username'))

    return HttpResponse(
        json.dumps({'task_id':task_obj.task.id,'selected_hosts':selected_hosts})
    )


@login_required
def multitask_result(request):
    '''获取结果'''
    task_id = request.GET.get('task_id')
    task_obj = models.Task.objects.get(id=task_id)
    task_log_results = list(task_obj.tasklogdetail_set.values('id', 'result','status','start_date','end_date'))

    return  HttpResponse(json.dumps(task_log_results,default=json_date_handler))


def json_date_handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.strftime("%Y-%m-%d %T")



