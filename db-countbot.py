# count-bots.py

"""
Description:

This script records the number of bots registered by the C&C server 
with the time elapsed (during DoS attack).

"""

import time
import MySQLdb

# Set time period between measurements (s)
PERIOD = 1
PROGRAM_START_TIME = 0

# Connection strings
HOST		= "10.0.0.128"
USER		= "psyche"
PASSWORD	= "psyche"
DB		= "4bnev"

# Connect to DB
db = MySQLdb.connect(host=HOST, user=USER, passwd=PASSWORD, db=DB)

# Create cursor object
cur = db.cursor(MySQLdb.cursors.DictCursor)

def get_bot_count():
	# SQL select
	select = "SELECT count(bid) AS count FROM bot WHERE lastseen > " \
		+ str(PROGRAM_START_TIME)

	cur.execute(select)
	row = cur.fetchone()

	return row["count"]

# Wait until at least one bot is registered before starting measurements
def wait_measurement():
	while True:
		count = get_bot_count()
		
		if count > 0:
			start = int(time.time())
			return start

def main():
	print "Bot counter v1.0\n"

	global PROGRAM_START_TIME

	PROGRAM_START_TIME = time.time()

	# Wait until first bot is registered
	print "[*] Waiting for bots to be registered..."
	measurement_start_time = wait_measurement()

	while True:
		# Calculate time elapsed
		now = int(time.time())
		time_elapsed = now - measurement_start_time

		count = get_bot_count()
	
		print "[+] Time elapsed:",time_elapsed, "s,\tcount:",  count

		time.sleep(PERIOD)


if __name__ == "__main__":
	main()

