# count-bot.py

"""
Description:

This program counts the number of bots registered in the botnet C&C.

Modules:

    cipher          : Defines the CBC encryption/decryption functions
    c_types_defines : Defines ctype structures
    termcolor       : For printing out colored text, $pip install termcolor

"""

import sys
import array
import socket
import fcntl
import struct
import time

from bot import init_socket
from cipher import pencrypt, pdecrypt
from utils import hexdump, get_ip_address
from c_types_defines import *
from termcolor import cprint
from progressbar import ProgressBar

# C&C connection IP and Port number
HOST = "10.0.0.128"
PORT = 43242

# Network interface of bot
IFACE   = "vmnet8"
TIMEOUT = 3

# C&C commands
RC_BID      = 5

# This function listens for the RC_BID command specifically.
# It is possible to use the process_package() from the bot module instead, but
# the function below is more efficient for this program.
def get_bid(s):
    while True:
        try:
            # Try receiving data
            rcvmsg = s.recv(1024)

            # Check whether connection is closed
	    if rcvmsg == "":
                break
	
            # Got server response:
            cmd = struct.unpack("i", rcvmsg[0:4])[0] 

            if cmd == RC_BID:
                # Decrypt data received
                dec = pdecrypt(rcvmsg[8:], len(rcvmsg[8:]))

                # Extract the BID from the decrypted data
                bid = struct.unpack("i", dec[0:4])[0] 
                return bid

        except socket.error as e:
            print "[-]", str(e)

def main():
    print "Bot counter v2.2\n"

    # Initialize bot_rheader structure
    bot_rheader = init_bot_rheader(bid=0, size=0)

    # Initialize socket
    s = init_socket(IFACE, TIMEOUT)

    # Send data (BOT_RHEADER packed binary)
    s.sendall(buffer(bot_rheader)[:])

    # Get BID upper bound
    upper_bound = get_bid(s)

    if not upper_bound:
        cprint("[-] Error: Failed to get BID upper bound", "red")
        sys.exit(-1)
    else:
        cprint("[+] Got BID upper bound: " + str(upper_bound), "green")

    # Give the user chance to see the upper bound
    time.sleep(3)

    cprint("\n[*] Starting bot counter...", "cyan")

    bot_count = 0           # Bot entry count
    bid_registered = []     # BID of bots registered
    bid_not_registered = [] # BID of bots not registered

    # Note: Max size of Python list is 536,870,912 elements (on a 32bit system).
    # Warning: The larger the list is the slower the operations will be.

    # Show progress bar
    pbar = ProgressBar()

    # Search And Destroy
    for bid in pbar(list(range(upper_bound - 1, 0, -1))):
        # Spoof BID
        bot_rheader.bid = bid

        s = init_socket(IFACE, TIMEOUT) # Re-initiate socket connection
        s.sendall(buffer(bot_rheader)[:]) # Send data

        # Check return BID
        if bid == get_bid(s):
            bot_count += 1
            bid_registered.append(bid) 
            #cprint("[BID: " + str(bid) + "]" + " Bot found\t\tTotal: " \
            #       + str(bot_count), "cyan")
        else:
            bid_not_registered.append(bid)
            #cprint("[BID: " + str(bid) + "]" + " Bot not registered", "red")

    # Print statistics
    cprint("\n[+] Statistics:", "yellow")
    cprint("Total bot count: " + str(bot_count), "yellow")
    cprint("\nBID registered:", "yellow")
    print "[%s]" % ", ".join(map(str, bid_registered))
    cprint("\nBID not registered:", "yellow")
    print "[%s]" % ", ".join(map(str, bid_not_registered))

    # Close socket
    s.close()

if __name__ == "__main__":
    main()

