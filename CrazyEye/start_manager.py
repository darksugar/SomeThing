#Authon Ivor

import os

if __name__ == "__main__":
    #启用django环境变量
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "CrazyEye.settings")
    #load所有app
    import django
    django.setup()
    from backend import main


    obj = main.HostManager()
    obj.interactive()
