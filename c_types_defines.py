# c_types_defines.py

"""
Description:

This program implements the following ctype structures:

    BOT_RHEADER     : from globals.h:24
    BOTBULK_INFO    : from spcntrl.h:111
    BOT_INFO        : from spcntrl.h:123

"""

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
		("mails",		POINTER(c_int)),
		("bulk_id",		c_int),
		("tmplver",		c_int),
		("cc_ver",		c_int),
		("count",		c_int),
		("accounts",		c_void_p), # TODO unsigned *accounts
		("accounts_send",	c_void_p), # TODO unsigned *accounts_send
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

"""
# Test code
b_rheader = BOT_RHEADER()
bbulk_info = BOTBULK_INFO()
b_info = BOT_INFO()
print "[+] TEST COMPLETE"
"""

