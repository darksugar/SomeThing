from django.db import models
from . import auth
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
# Create your models here.

#机房
class IDC(models.Model):
    name = models.CharField(max_length=64,unique=True)

    def __str__(self):
        return self.name
    class Meta:
        verbose_name = 'IDC'
        verbose_name_plural = 'IDC'

#用户分组
class Department(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '部门'
        verbose_name_plural = '部门'

#主机信息
class Hosts(models.Model):
    hostname = models.CharField(max_length=64,unique=True)
    ip_addr = models.GenericIPAddressField(unique=True)
    system_type_choices = (
        ('windows','Windows'),
        ('linux', 'Linux/Unix')
    )
    idc = models.ForeignKey('IDC',on_delete = models.CASCADE)
    system_type = models.CharField(choices=system_type_choices,max_length=32,default='linux')
    port = models.IntegerField(default=22)
    enabled = models.BooleanField(default=True,help_text='主机若不想被用户访问可以去掉此选项')
    memo = models.CharField(max_length=128,blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s(%s)' %(self.hostname,self.ip_addr)

    class Meta:
        verbose_name = '主机'
        verbose_name_plural = '主机'

#远程主机用户名及密码
class HostUsers(models.Model):
    auth_method_choices = (('ssh-password',"SSH/ Password"),('ssh-key',"SSH/KEY"))
    auth_method = models.CharField(choices=auth_method_choices,max_length=16,help_text='如果选择SSH/KEY，请确保你的私钥文件已在settings.py中指定')
    username = models.CharField(max_length=32)
    password = models.CharField(max_length=64,blank=True,null=True,help_text='如果auth_method选择的是SSH/KEY,那此处不需要填写..')
    memo = models.CharField(max_length=128,blank=True,null=True)

    def __str__(self):
        return '%s(%s)' %(self.username,self.password)

    class Meta:
        verbose_name = '远程主机用户'
        verbose_name_plural = '远程主机用户'
        unique_together = ('auth_method','password','username')

#绑定远程主机和远程用户的对应关系
class BindHosts(models.Model):
    host = models.ForeignKey('Hosts',on_delete = models.CASCADE)
    host_user = models.ForeignKey('HostUsers',verbose_name="远程用户",on_delete = models.CASCADE)

    enabled = models.BooleanField(default=True)

    def __str__(self):
        return '%s:%s' %(self.host,self.host_user)
        # return '%s:%s' %(self.host.hostname,self.host_user.username)

    class Meta:
        unique_together = ("host", "host_user")
        verbose_name = '主机与远程用户绑定'
        verbose_name_plural = '主机远程与用户绑定'

# 主机分组信息
class BindHostGroups(models.Model):
    name = models.CharField(max_length=64, unique=True)
    memo = models.CharField(max_length=128, blank=True, null=True)
    bind_hosts = models.ManyToManyField('BindHosts', blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '主机组'
        verbose_name_plural = '主机组'

#堡垒机的用户名及密码
class UserProfile(auth.AbstractBaseUser, auth.PermissionsMixin):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    password = models.CharField(_('password'), max_length=128,
                     help_text=mark_safe('''<a class='btn-link' href='password'>重置密码</a>'''))

    name = models.CharField(max_length=32)
    # token = models.CharField('token', max_length=128,default=None,blank=True,null=True)
    department = models.ForeignKey('Department', verbose_name='部门', blank=True, null=True,on_delete = models.CASCADE)
    bind_hosts_groups = models.ManyToManyField('BindHostGroups', verbose_name='授权主机组', blank=True)
    bind_hosts = models.ManyToManyField('BindHosts', verbose_name='授权主机', blank=True)

    memo = models.TextField('备注', blank=True, null=True, default=None)
    date_joined = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    valid_begin_time = models.DateTimeField(default=timezone.now, help_text="yyyy-mm-dd HH:MM:SS")
    valid_end_time = models.DateTimeField(blank=True, null=True, help_text="yyyy-mm-dd HH:MM:SS")

    USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = ['name','token','department','tel','mobile','memo']
    REQUIRED_FIELDS = ['name']
    objects = auth.UserManager()

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(
        verbose_name='staff status',
        default=True,
        help_text='Designates whether the user can log into this admin site.',
    )

    def __str__(self):  # __str__ on Python 2
        return "%s-->%s" % (self.email,self.name)
    def get_full_name(self):
        # The user is identified by their email address
        return self.email
    def get_short_name(self):
        # The user is identified by their email address
        return self.email
    # def has_perm(self, perm, obj=None):
    #     "Does the user have a specific permission?"
    #     # Simplest possible answer: Yes, always
    #     return True
    def has_perms(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True
    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True
    # @property
    # def is_staff(self):
    #     "Is the user a member of staff?"
    #     # Simplest possible answer: All admins are staff
    #     return self.is_admin
    @property
    def is_superuser(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

    class Meta:
        verbose_name = '用户账户信息'
        verbose_name_plural = u"用户账户信息"

        permissions = (
            ('web_access_dashboard', '可以访问 审计主页'),
            ('web_batch_cmd_exec', '可以访问 批量命令执行页面'),
            ('web_batch_batch_file_transfer', '可以访问 批量文件分发页面'),
            ('web_config_center', '可以访问 堡垒机配置中心'),
            ('web_config_items', '可以访问 堡垒机各配置列表'),
            ('web_invoke_admin_action', '可以进行admin action执行动作'),
            ('web_table_change_page', '可以访问 堡垒机各配置项修改页'),
            ('web_table_change', '可以修改 堡垒机各配置项'),
        )

class Session(models.Model):
    '''生成用户操作session id '''
    user = models.ForeignKey('UserProfile',on_delete = models.CASCADE)
    bind_host = models.ForeignKey('BindHosts',on_delete = models.CASCADE)
    tag = models.CharField(max_length=128, default='n/a')
    closed = models.BooleanField(default=False)
    cmd_count = models.IntegerField(default=0)  # 命令执行数量
    stay_time = models.IntegerField(default=0, help_text="每次刷新自动计算停留时间", verbose_name="停留时长(seconds)")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '<id:%s user:%s bind_host:%s>' % (self.id, self.user.email, self.bind_host.host)

    class Meta:
        verbose_name = '审计日志'
        verbose_name_plural = '审计日志'

class Task(models.Model):
    """批量任务记录表"""
    user = models.ForeignKey("UserProfile")
    task_type_choices = ((0, 'cmd'), (1, 'file_transfer'))
    task_type = models.SmallIntegerField(choices=task_type_choices)
    content = models.TextField(verbose_name="任务内容")
    # hosts = models.ManyToManyField("BindHost")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s %s" % (self.task_type, self.content)

class TaskLogDetail(models.Model):
    task = models.ForeignKey("Task")
    bind_host = models.ForeignKey("BindHosts")
    result = models.TextField()

    status_choices = ((0, 'success'), (1, 'failed'), (2, 'init'))
    status = models.SmallIntegerField(choices=status_choices)

    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return "%s %s" % (self.bind_host, self.status)


# class UserProfile(auth.AbstractBaseUser, auth.PermissionsMixin):
#     email = models.EmailField(
#         verbose_name='email address',
#         max_length=255,
#         unique=True,
#     )
#     password = models.CharField(_('password'), max_length=128,
#                                 help_text=mark_safe('''<a class='btn-link' href='password'>重置密码</a>'''))
#     name = models.CharField(max_length=32)
#     bind_hosts = models.ManyToManyField('BindHost',blank=True,null=True)
#     hostgroup  = models.ManyToManyField('HostGroup',blank=True,null=True)
#
#
#     is_active = models.BooleanField(default=True)
#     is_admin = models.BooleanField(default=False)
#     is_staff = models.BooleanField(
#         verbose_name='staff status',
#         default=True,
#         help_text='Designates whether the user can log into this admin site.',
#     )
#
#     USERNAME_FIELD = 'email'
#     # REQUIRED_FIELDS = ['name','token','department','tel','mobile','memo']
#     REQUIRED_FIELDS = ['name']
#
#     def get_full_name(self):
#         # The user is identified by their email address
#         return self.email
#     def get_short_name(self):
#         # The user is identified by their email address
#         return self.email
#     def __str__(self):  # __str__ on Python 2
#         return self.email
#     def has_perms(self, perm, obj=None):
#         "Does the user have a specific permission?"
#         # Simplest possible answer: Yes, always
#         return True
#     def has_module_perms(self, app_label):
#         "Does the user have permissions to view the app `app_label`?"
#         # Simplest possible answer: Yes, always
#         return True
#     @property
#     def is_superuser(self):
#         "Is the user a member of staff?"
#         # Simplest possible answer: All admins are staff
#         return self.is_admin
#     objects = auth.UserManager()
#
#     class Meta:
#         verbose_name = '自定义用户认证'
#         verbose_name_plural = '自定义用户认证'
#
#         permissions = (
#         # )