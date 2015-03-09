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

from cipher import pencrypt, pdecrypt
from c_types_defines import *
from termcolor import cprint

# C&C connection IP and Port number
# Test: nc -l 8080 | hexdump -C
#HOST = "127.0.0.1"
HOST = "172.16.211.134"
PORT = 43242

# C&C commands
RC_BID      = 5

# Dump combined hex/ascii rep of a packed binary string
# [Credit: code.activestate.com]
FILTER = "".join([(len(repr(chr(x))) == 3) and chr(x) or "." for x in range(256)])

def hexdump(src, length=16):
    result = []
    
    for i in xrange(0, len(src), length):
        s = src[i:i+length]
	hexa = " ".join(["%02X" % ord(x) for x in s])
	printable = s.translate(FILTER)
	result.append("%04X\t%-*s\t%s\n" % (i, length*3, hexa, printable))

    return "".join(result)

# Get the IP address for a particular interface
# [Credit: www.quora.com]
def get_ip_address(iface):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
                s.fileno(),
                0x8915, # SIOCGIFADDR
                struct.pack("256s", iface[:15])
            )[20:24])


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

def init_socket():
    # Socket configurations
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((get_ip_address("vmnet8"), 0))
    s.settimeout(3.0) # Set 3s timeout

    # Connect
    s.connect((HOST, PORT))

    return s

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
    s.close()

    return bid[0]

def main():
    # Initialize bot_rheader structure
    init_bot_rheader()

    # Initialize socket
    s = init_socket()

    # Send data (BOT_RHEADER packed binary) TODO: bot_info
    data = buffer(bot_rheader)[:] * 2
    s.sendall(data)

    # Get BID upper bound
    upper_bound = get_bid(s)

    if not upper_bound:
        cprint("[-] Error: Failed to get BID upper bound", "red")
        exit(-1)
    else:
        cprint("[+] Got BID upper bound: " + str(upper_bound), "green")

    # Give the user chance to see the upper bound
    sleep(3)

    # Bot entry count
    bot_count = 0

    # BID of bots registered
    bid_registered = []

    # BID of bots not registered
    bid_not_registered = []

    # Search And Destroy
    for bid in range(upper_bound - 1, 0, -1):
        # Spoof BID
        bot_rheader.bid = bid

        # Re-initiate socket connection
        s = init_socket()

        # Send data TODO: bot_info
        data = buffer(bot_rheader)[:] * 2
        s.sendall(data)

        # Check return BID
        if bid == get_bid(s):
            bot_count += 1
            bid_registered.append(bid) 
            cprint("[BID: " + str(bid) + "]" + " Bot found\t\tTotal: " \
                    + str(bot_count), "cyan")
        else:
            bid_not_registered.append(bid)
            cprint("[BID: " + str(bid) + "]" + " Bot not registered", "red")

if __name__ == "__main__":
    main()

