#!/usr/bin/env python
# -*- coding:utf-8 -*-

import socket
import fcntl
import struct, sys  

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ipaddr = socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15]))[20:24])
    return ipaddr

def get_netmask(ifname):
    return socket.inet_ntoa(fcntl.ioctl(
        socket.socket(socket.AF_INET, socket.SOCK_DGRAM),
        35099,
        struct.pack('256s', ifname))[20:24])

def get_default_gateway_linux():
    with open("/proc/net/route") as fh:
        for line in fh:
            fields = line.strip().split()
            if fields[1] != '00000000' or not int(fields[3], 16) & 2:
                continue
            return socket.inet_ntoa(struct.pack("<L", int(fields[2], 16)))

def get_dns(dns_number="1"):
    counter = 0
    with open("/etc/resolv.conf") as f:
        content = f.readlines()
        for line in content:
            if "nameserver " in line:
                counter= counter+1
                if (str(counter) == dns_number):
                    return line[11:len(line)-1];

def change_addr(ipaddr, ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ipaddr = socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15]))[20:24])



if __name__ == "__main__":
    for item in sys.argv:
        if len(sys.argv) == 3:
            if item.split('=')[0] == "--ipaddr" and item.split('=')[0] == "--net":
                change_addr(item.split('=')[1], ifname)
        elif len(sys.argv) == 2:
            if item.split('=')[0] == "--net" and len(sys.argv) == 1:
                print(get_ip_address(item.split('=')[1]))
        elif '=' in item :
            print("The args is Error! The args is %s" % item)
            

