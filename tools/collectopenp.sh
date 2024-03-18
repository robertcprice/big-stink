#!/bin/bash
#This script collects all open ports on a network and outputs 
#them into a file to be used with other scripts in suite

nmap -sS -p 1-1024 -oG - 192.168.1.1 | grep '/open/' | awk '{print $1}' > open_ports.txt