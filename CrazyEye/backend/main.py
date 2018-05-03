#Authon Ivor
from django.contrib.auth import authenticate
import subprocess,uuid
from web import models

class HostManager(object):
    '''用户登陆堡垒机后的交互脚本'''

    def __init__(self):
        self.user = None

    def get_session_id(self, bind_host_obj, tag):
        '''生成session记录并返回id'''
        session_obj = models.Session(user_id=self.user.id, bind_host=bind_host_obj, tag=tag)
        session_obj.save()
        return session_obj

    def interactive(self):
        '''交互脚本'''
        print("Please Login".center(50, '-'))
        count = 0
        while count < 3:
            username = input("请输入用户名:").strip()
            password = input("请输入密码:").strip()
            user = authenticate(username=username,password=password)
            if user:
                print("Welcome %s".center(50,'-') % self.user)
                self.user = user
            else:
                count += 1
            if self.user:
                #进入已登陆用户的交互菜单
                while True:
                    # 打印当前用户的所有组以及绑定的主机
                    user_groups = self.user.bind_hosts_groups
                    for group_index,group_obj in enumerate(user_groups.all()):
                        print("%s.\t%s[%s]" % (group_index,group_obj.name,group_obj.bind_hosts.count()) )
                    print("z. \t未分组主机[%s]" % (self.user.bind_hosts.count()))
                    print("q. \tExit")
                    choice = input(">>>:")
                    if not choice.strip():continue
                    #判断选项
                    selected_group = None
                    if choice.isdigit():
                        choice = int(choice)
                        if choice >= 0 and choice <= group_index:
                            #打印所选择组当中的所有主机
                            selected_group = self.user.bind_hosts_groups.all()[choice]
                    elif choice == "z":
                            selected_group = self.user
                    elif choice == 'q':
                        exit("Bye".center(50, '-'))

                    if selected_group:
                        while True:
                            for host_index, host_obj in enumerate(selected_group.bind_hosts.all()):
                                print("%s.\t%s" % (host_index, host_obj) )
                            # 进入主机选择菜单
                            choice = input(">>>:")
                            if choice.isdigit():
                                choice = int(choice)
                                if choice >= 0 and choice <= host_index:
                                    selected_host = selected_group.bind_hosts.all()[choice]
                                    ssh_tag = uuid.uuid4()
                                    session_obj = self.get_session_id(selected_host, ssh_tag)
                                    obj = subprocess.Popen(
                                        "sh /usr/local/CrazyEye/backend/session_tracker.sh %s %s" %
                                        (ssh_tag,
                                         session_obj.id), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        shell=True, )
                                    subprocess.run("sshpass -p %s ssh %s@%s -i %s" %
                                                   (selected_host.host_user.password,
                                                    selected_host.host_user.username,
                                                    selected_host.host.ip_addr,
                                                    ssh_tag,),
                                                   shell=True)
                            elif choice == 'b':
                                break
                            elif choice == 'q':
                                exit("Bye".center(50, '-'))

                    # # 打印未分组主机 已经把两段合并
                    # elif choice == 'z':
                    #     for unbind_host_index,unbind_host_obj in enumerate(self.user.bind_hosts.all()):
                    #         print("%s.\t%s" % (unbind_host_index, unbind_host_obj))
                    #         #进入未分组主机选择菜单
                    #     while True:
                    #         choice = input(">>>:")
                    #         if choice.isdigit():
                    #             choice = int(choice)
                    #             if choice >= 0 and choice <= unbind_host_index:
                    #                 selected_unbind_host = self.user.bind_hosts.all()[choice]
                    #                 ssh_tag = uuid.uuid4()
                    #                 session_obj = self.get_session_id(selected_unbind_host, ssh_tag)
                    #                 obj = subprocess.Popen("sh /usr/local/CrazyEye/backend/session_tracker.sh %s %s" %
                    #                                (ssh_tag,
                    #                                 session_obj.id),
                    #                                 # stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                    #                                 shell=True,)
                    #
                    #                 subprocess.run("sshpass -p %s ssh %s@%s -i %s -o  StrictHostKeyChecking=no" %
                    #                                (selected_unbind_host.host_user.password,
                    #                                 selected_unbind_host.host_user.username,
                    #                                 selected_unbind_host.host.ip_addr,
                    #                                 ssh_tag,
                    #                                 ),
                    #                                shell=True)
                    #         elif choice == 'b':
                    #             break
                    #         elif choice == 'q':
                    #             exit("Bye".center(50, '-'))
                    # #退出
                    # elif choice == 'q':
                    #     exit("Bye".center(50,'-'))


