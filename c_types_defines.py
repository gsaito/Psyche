# c_types_defines.py

"""
Description:

This program implements the following ctype structures:

    BOT_RHEADER     : from globals.h:24
    BOTBULK_INFO    : from spcntrl.h:111
    BULK_INFO       : from spcntrl.h:255
    BOT_INFO        : from spcntrl.h:123

"""

import sys
from ctypes import *

# General recv header
class BOT_RHEADER(Structure):
	_fields_ = [
		("bid",		c_int),
		("iplocal",	c_int),
		("botver",	c_int),
		("confver",	c_int),
		("mfver",	c_int),
		("winver",	c_int),
		("flags",	c_short), # 5IIUERHH
		("smtp",	c_short),
		("size",	c_int),
		]

class BOTBULK_INFO(Structure):
	_fields_ = [
		#("mails",		POINTER(c_int)),
		("bulk_id",		c_int),
		("tmplver",		c_int),
		("cc_ver",		c_int),
		("logsize",		c_int),
		("addrsize",		c_int),
		#("count",		c_int),
		#("accounts",		c_void_p), 
		#("accounts_send",	c_void_p), 
		]

class BULK_INFO(Structure):
	_fields_ = [
		("id",		        c_int),
		("state",		c_int),
		]

class BOT_INFO(Structure):
	_fields_ = [
		("ip",			c_char * 4),
		("have_ip",		c_int),

		("bufsend",		c_char_p),
		("bufrecv",		c_char_p),
		("bufdata",		c_char_p),
		("bufsmall",		c_int),

		("id",			c_int),
		("bid",			c_int),
		("sd",			c_int),
		("bufsize",		c_int),
		("timer",		c_int),
		("state",		c_int),
		("blackliststatus",	c_int),
		("bshcommand",		c_int),

		("flags",		c_short),

		("botbulk",		POINTER(BOTBULK_INFO)),

		# Statistics
		("bsent",		c_longlong),
		("bnouser",		c_longlong),
		("bunlucky",		c_longlong),
		("bunksmtpansw",	c_longlong),
		("bblacklisted",	c_longlong),
		("bmailfrombad",	c_longlong),
		("bgraylisted",		c_longlong),
		("bnomx",		c_longlong),
		("bnomxip",		c_longlong),
		("bnoaliveip",		c_longlong),
		("bsmtptimeout",	c_longlong),
		("bconnect",		c_longlong),
		("brecv",		c_longlong),
		("bbotmailtimeout",	c_longlong),
		("bspammessage",	c_longlong),
		("bnohostname",		c_longlong),
		("blckmx",		c_longlong),

		("captcha_good",	c_longlong),
		("captcha_total",	c_longlong),

		("refbulk",		POINTER(c_int)),
		("refbulk_size",	c_int),
		]

# Initialise bot_rheader structure
def init_bot_rheader(bid=0, size=0):
    bot_rheader             = BOT_RHEADER()

    bot_rheader.bid         = bid 
    bot_rheader.iplocal     = 97718444 # Should be INT
    bot_rheader.botver      = 116 
    bot_rheader.confver     = 198 
    bot_rheader.mfver       = 1 
    bot_rheader.winver      = 5 
    bot_rheader.flags       = 1 # ERZ: 8, R5+HOSTNAME: 129, DEFAULT: 0
    bot_rheader.smtp        = 1 
    bot_rheader.size        = size

    return bot_rheader

# Initialise botbulk_info structure
def init_botbulk_info(bulk_id=0, logsize=0):
    botbulk_info            = BOTBULK_INFO()

    botbulk_info.bulk_id    = bulk_id 
    botbulk_info.tmplver    = 1 
    botbulk_info.cc_ver     = 198 
    botbulk_info.logsize    = logsize
    botbulk_info.addrsize   = 0 

    return botbulk_info

# Initialize bulk_info structure
def init_bulk_info(id, state):
    bulk_info               = BULK_INFO()

    bulk_info.id            = id
    bulk_info.state         = state # SENT: 1, BLACKLISTED: 5

    return bulk_info

"""
# Test code
try:
    bot_rheader     = init_bot_rheader()
    botbulk_info    = init_botbulk_info()
    bulk_info       = init_bulk_info()
except Exception as e:
    sys.exit(str(e))
print "[+] TEST COMPLETE"
"""

