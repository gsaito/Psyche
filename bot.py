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

# C&C connection IP and Port number
# Test: nc -l 8080 | hexdump -C
#HOST = "127.0.0.1"
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

# Initialise bot_rheader, botbulk_info, and bulk_info structures
bot_rheader = BOT_RHEADER()
botbulk_info = BOTBULK_INFO()
bulk_info = BULK_INFO()

# Flags
RC_SLEEP_OK = False

def process_package(rcvmsg, rtt):
    # Interpret RC command (1-9)
    cmd = ord(rcvmsg[0])

    if cmd in range(1,10):
        sys.stdout.write("[+] Received (RTT: " + str(rtt * 1000) \
                + "ms, Pkg size: " + str(len(rcvmsg)) + "): ")

    if   cmd == RC_SLEEP:
        cprint("RC_SLEEP",      "cyan")
        RC_SLEEP_OK = True
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
        cprint("Decryption:\n" + hexdump(dec), "yellow")

    # Command actions
    if cmd == RC_BID:
        # Extract the BID from the decrypted data
        bid = struct.unpack("i", dec[0:4]) # Returns a tuple

        # Extract sign.timer from the decrypted data
        timer = struct.unpack("i", dec[8:12])

        cprint("[+] Assigned BID: " + str(bid[0]) \
                + ", Timer: " + str(timer[0]) + "\n", "green")

        # Update BOT_RHEADER structure
        bot_rheader.bid = bid[0]

def bulk_info_factory(id, state):
    bi = BULK_INFO()
    bi.id = id
    bi.state = state
    return buffer(bi)[:]

def main():
    # Socket configurations
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((get_ip_address("vmnet8"), 0))
    s.settimeout(3.0) # Set 3s timeout

    # Connect
    s.connect((HOST, PORT))

    print "Cutwail Bot Clone v5.1"
    cprint("\n[*] Sending data to " + HOST + " : " + str(PORT) \
            + " (hexdump below)\n", "green")

    # Populate bot_rheader structure
    bot_rheader.bid             = 32534
    bot_rheader.iplocal         = 97718444 # Should be INT
    bot_rheader.botver          = 116
    bot_rheader.confver         = 198
    bot_rheader.mfver           = 1
    bot_rheader.winver          = 5
    bot_rheader.flags           = 1 # ERZ: 8, R5+HOSTNAME: 129, DEFAULT: 0
    bot_rheader.smtp            = 1
    bot_rheader.size            = len(buffer(botbulk_info)[:])

    # Populate botbulk_info structure
    botbulk_info.bulk_id        = 1
    botbulk_info.tmplver        = 1
    botbulk_info.cc_ver         = 198
    botbulk_info.logsize        = 0
    botbulk_info.addrsize       = 0

    # Populate bulk_info structure
    bulk_info.id                = 0
    bulk_info.state             = 5 # SENT: 1, BLACKLISTED: 5

    # Construct data package
    data = buffer(bot_rheader)[:] \
            + pencrypt(buffer(botbulk_info)[:], len(buffer(botbulk_info)[:]))

    # Print package content
    cprint("BOT_RHEADER\n", "yellow"); print hexdump(buffer(bot_rheader)[:])
    cprint("BOTBULK_INFO\n", "yellow"); print hexdump(buffer(botbulk_info)[:])
    cprint("BULK_INFO\n", "yellow"); print hexdump(buffer(bulk_info)[:])
    cprint("DATA\n", "yellow"); print hexdump(data)
    
    # Send data package
    s.sendall(data)
    cprint("[+] Sent! Now waiting to receive data...\n", "green")

    # Initialise recv buffer
    buf = ""

    # Start timer
    start = time.clock()

    # Listen on host
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
            end = time.clock()  # Stop timer
            rtt = end - start   # Compute RTT

            # Let's check out the contents of recv buffer (if not empty)
            if buf:
                # Process package
                process_package(buf, rtt)

                # Send back statistics:
                cprint("\n[*] Send back data package...\t" \
                            + "(press ENTER to continue) ", "green", end=""); 

                raw_input("")
                
                """
                cprint("\n[*] Ready to send data package... ", "green"); 
                state = int(raw_input("Enter state > "))
                if state not in range(1, 10):
                    state = 1
                """
                
                # Create a BULK_INFO array
                bulk_info_array = ""
                for i in range(0, 2):
                    bulk_info_array += bulk_info_factory(i, 5)

                # Ajust the size fields of botbulk_info and bot_rheader accordingly
                botbulk_info.logsize = i + 1
                bot_rheader.size = len(buffer(botbulk_info)[:]) \
                                    + len(buffer(bulk_info)[:]) * botbulk_info.logsize

                # Construct data package
                data = buffer(bot_rheader)[:] \
                        + pencrypt(buffer(botbulk_info)[:] \
                                + bulk_info_array, bot_rheader.size)

                cprint("\nDATA\n", "yellow"); print hexdump(data)
                start = time.clock() # Restart timer
                s.sendall(data)

                # Clear recv buffer
                buf = ""
                cprint("\n[*] Listening for incoming data...\t(press Ctrl+C to quit)\n" \
                        , "green")

    # Close socket
    s.close()

if __name__ == "__main__":
    main()

