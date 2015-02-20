# cipher.py

"""
Description:

This module implements the CBC encryption scheme as in pcrypt.c

"""

import sys
import array

# CBC keys
PKEY_SIZE = 29
encrypt_key = "Poshel-ka ti na hui drug aver"
decrypt_key = "reva gurd iuh an it ak-lehsoP"

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

