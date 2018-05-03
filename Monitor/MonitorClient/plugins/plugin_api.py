#_*_coding:utf-8_*_
__author__ = 'Alex Li'

from linux import sysinfo,load,cpu_mac,cpu,memory,network,host_alive



def LinuxCpuPlugin():
    return cpu.monitor()

def host_alive_check():
    return host_alive.monitor()

def GetMacCPU():
    #return cpu.monitor()
    return cpu_mac.monitor()

def LinuxNetworkPlugin():
    return network.monitor()

def LinuxMemoryPlugin():
    return memory.monitor()


def get_linux_load():
    return load.monitor()