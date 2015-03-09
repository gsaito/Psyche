# bot.py

"""
Description:

This program connects and communicates with the botnet C&C.

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
RC_SLEEP    = 1
RC_GETWORK  = 2
RC_RESTART  = 3
RC_UPDATE   = 4
RC_BID      = 5
RC_TEMPLATE = 6
RC_CONFIG   = 7
RC_MAILFROM = 8
RC_ACCOUNTS = 9

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

def main():
    # Socket configurations
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #s.setsockopt(socket.SOL_SOCKET, 25, "vmnet8") # SO.BINDTODEVICE (25)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((get_ip_address("vmnet8"), 0))
    s.settimeout(3.0) # Set 3s timeout

    # Connect
    s.connect((HOST, PORT))

    cprint("\n[*] Sending data to " + HOST + " : " + str(PORT) \
            + " (hexdump below)\n", "green")

    # Initialise bot_info, bot_rheader, botbulk_info structures
    bot_info = BOT_INFO()
    bot_rheader = BOT_RHEADER()
    botbulk_info = BOTBULK_INFO()

    # Populate bot_rheader structure
    bot_rheader.bid     = 1
    bot_rheader.iplocal = 97718444 # Should be INT
    bot_rheader.botver  = 116
    bot_rheader.confver = 198
    bot_rheader.mfver   = 1
    bot_rheader.winver  = 1
    bot_rheader.flags   = 0
    bot_rheader.smtp    = 1
    bot_rheader.size    = 32

    # Conversion: Structure -> Bytes (Str)
    #bot_info.bufrecv = buffer(bot_rheader)[:] # Same as pack()

    # Populate bot_info structure
    bot_info.ip                 = "\254\020\323\003" # char[4]
    bot_info.have_ip            = 1
    bot_info.bufsize            = 32
    bot_info.bid                = 0
    bot_info.timer              = 1425851228
    bot_info.state              = 80 # BSTBULKOK
    bot_info.bshcommand         = RC_UPDATE
    bot_info.sd                 = 10
    bot_info.bufsmall           = 0
    
    bot_info.bsent              = 1

    """
    bot_info.bufsend            = ""
    bot_info.bufrecv            = ""
    bot_info.bufdata            = ""

    bot_info.id                 = 0
    bot_info.blackliststatus    = 0

    bot_info.flags              = 0

    bot_info.botbulk            = pointer(botbulk_info)

    # Statistics
    bot_info.bnouser            = 0
    bot_info.bunlucky           = 0
    bot_info.bunksmtpansw       = 0
    bot_info.bblacklisted       = 0
    bot_info.bmailfrombad       = 0
    bot_info.bgraylisted        = 0
    bot_info.bnomx              = 0
    bot_info.bnomxip            = 0
    bot_info.bnoaliveip         = 0
    bot_info.bsmtptimeout       = 0
    bot_info.bconnect           = 0
    bot_info.brecv              = 0
    bot_info.bbotmailtimeout    = 0
    bot_info.bspammessage       = 0
    bot_info.bnohostname        = 0
    bot_info.blckmx             = 0

    bot_info.captcha_good       = 0
    bot_info.captcha_total      = 0

    refbulk = (c_byte * 4)()
    bot_info.refbulk            = cast(refbulk, POINTER(c_int)) # NULL
    bot_info.refbulk_size       = 0
    """

    # Send data (BOT_RHEADER followed by BOT_INFO)
    data = buffer(bot_rheader)[:] + buffer(bot_info)[:]
    print hexdump(data)
    s.sendall(data)
    cprint("[+] Sent! Now waiting to receive data...\n", "green")

    # Initialise recv buffer
    buf = ""

    # Flags
    skip = False

    # Listen on host
    while True:

        try:
            # Try receiving data
            rcvmsg = s.recv(1024)

            # Check whether connection is closed
	    if rcvmsg == "":
	        break
	
            # Got some data!
            sys.stdout.write("[+] Received: ")

            # Interpret command
            cmd = ord(rcvmsg[0])

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

	    print hexdump(rcvmsg)

            # Command actions
            if cmd == RC_BID:
                # Decrypt data received
                dec = pdecrypt(rcvmsg[8:], len(rcvmsg[8:]))
                cprint("Decryption:\n" + hexdump(dec), "yellow")

                # Extract the BID from the decrypted data
                bid = struct.unpack("i", dec[0:4]) # Returns a tuple

                # Extract sign.timer from the decrypted data
                timer = struct.unpack("i", dec[8:12])

                cprint("[+] Assigned BID: " + str(bid[0]) \
                        + ", Timer: " + str(timer[0]) + "\n", "green")

                # Update BOT_RHEADER and BOT_INFO structures
                bot_rheader.bid = bid[0]
                bot_info.bid = bid[0]
                bot_info.timer = timer[0]

            """
            if cmd == RC_UPDATE and not skip:
                cprint("[*] Sending updated data...", "yellow")
                data = buffer(bot_rheader)[:] + buffer(bot_info)[:]
                print hexdump(data)
                s.sendall(data)
                skip = True
            """

            # Store data in buffer (for later use)
            buf += rcvmsg
        
        except socket.timeout:

            # Timed out on receiving data: 
            # Let's check out the contents of recv buffer (if not empty)
            if buf:
                # Decrypt recv buffer
                #dec = pdecrypt(buf, len(buf))
                #print "[+] Decrypted:\n", dec, "\n"

                # Clear recv buffer
                buf = ""
                cprint("[*] Listening for incoming data (press Ctrl+C to quit)\n" \
                        , "green")

    # Close socket
    s.close()

if __name__ == "__main__":
    main()

