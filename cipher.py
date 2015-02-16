# cipher.py

import array
import socket
import sys

from c_types_defines import *

PKEY_SIZE = 29

encrypt_key = "Poshel-ka ti na hui drug aver"
decrypt_key = "reva gurd iuh an it ak-lehsoP"

# Test: nc -l 8080 | hexdump -C
#HOST = "127.0.0.1"
HOST = "172.16.211.134"
PORT = 43242

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
    s.settimeout(5.0) # set 5s timeout

    # Connect
    s.connect((HOST, PORT))

    print "[*] Sending data to", HOST, ":", PORT

    # Initialise bot_info and bot_rheader structures
    bot_info = BOT_INFO()
    bot_rheader = BOT_RHEADER()

    # Populate bot_rheader structure
    bot_rheader.bid = 1
    bot_rheader.iplocal = 4321 # Should be INT, "\xac\x10\xd3\x01"
    bot_rheader.botver = 1
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
    bot_info.bufrecv = bufrecv_enc

    # Send
    print "[*] Hexdump(data):\n", hexdump(buffer(bot_info)[:])
    s.sendall(buffer(bot_info)[:])
    print "[+] Sent!\n"

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
	
            # Got some data
	    print "[+] Received:\n", hexdump(rcvmsg)
            buf += rcvmsg

        except socket.timeout:

            # Timed out on receiving data: 
            # Let's check out the contents of recv buffer (if not empty)
            if buf:
                # Decrypt recv buffer
                dec = pdecrypt(buf, len(buf))
                print "[+] Decrypted:\n", dec, "\n"

                # Clear recv buffer
                buf = ""
                print "[*] Listening for incoming data (press Ctrl+C to quit)"

    # Close socket
    s.close()

if __name__ == "__main__":
    main()

