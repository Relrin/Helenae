import sys
import os
import platform

from json import dumps, loads

from optparse import OptionParser

from twisted.python import log
from twisted.internet import reactor, ssl

from autobahn.twisted.websocket import WebSocketClientFactory, WebSocketClientProtocol, connectWS

# TODO: Create plugins for future commands
# TODO: Define commands for USER (auth, read/write/sync files, etc.)
# TODO: Add methods/commands into ServerClientSSL

class DFSClientProtocol(WebSocketClientProtocol):

    commands = {"AUTH": "autorization with server",
                "READ": "read some file from storage",
                "WRTE": "write file into storage",
                "DELT": "delete file from storage",
                "RNME": "rename file",
                "LIST": "get list of all files from storage with this user",
                "SYNC": "synchronize all files with storage on the server",
                "EXIT": "disconnect from server or end session"}

    def __init__(self):
        self.counterAttemptsLogin = 3

    def mainMenu(self):
        """
            Print available commands into console
        """
        print "Available commands:"
        for cmd in sorted(self.commands.keys()):
            print "\t%s \t %s" % (cmd, self.commands[cmd])

    def inputData(self):
        """
            Input login and pass from keyboard for auth
        """
        login = raw_input('Login:')
        password = raw_input('Password:')
        hash_password = str(hash(password))
        return login, hash_password

    def constructData(self, cmd, user, hash, auth, error=''):
        """
            Create JSON for server
        """
        data = {}
        data['cmd'] = cmd
        data['user'] = user
        data['password'] = hash
        data['auth'] = auth
        data['error'] = error
        return dumps(data)

    def onOpen(self):
        """
            Send auth request to server, when create connection
        """
        login, hash_password = self.inputData()
        data = dumps({'cmd': 'AUTH', 'user': login, 'password': hash_password, 'auth': False, 'error': ''})
        self.sendMessage(str(data))

    def onMessage(self, payload, isBinary):
        """
            Processing responses from server and send new requests to there
        """
        data = loads(payload)
        # for none-authorized users commands
        if data['auth'] == False:
            # error in login or password --> try again...
            if data['cmd'] == 'RAUT':
                if self.counterAttemptsLogin > 0:
                    print '\nError: %s' % data['error']
                    print 'Attempts left: %d\n' % self.counterAttemptsLogin
                    self.counterAttemptsLogin -= 1
                    login, hash_password = self.inputData()
                    data = self.constructData('AUTH', login, hash_password, False)
                else:
                    print '\nTrying to hacking account or DDoS server? I will stop YOU!'
                    reactor.stop()
        # for authorized users commands
        else:
            # clear console at show main menu
            if platform.system() == "Linux":
                # its Linux/MacOS
                os.system('clear')
            else:
                # its Windows
                os.system('cls')
            self.mainMenu()
            cmd = ''
            while cmd not in self.commands.keys():
                cmd = raw_input('Command: ')
            if cmd == 'AUTH':
                self.counterAttemptsLogin = 3
                login, hash_password = self.inputData()
                data = self.constructData('AUTH', login, hash_password, False)
            elif cmd == 'READ':
                pass
            elif cmd == 'WRTE':
                pass
            elif cmd == 'DELT':
                pass
            elif cmd == 'RNME':
                pass
            elif cmd == 'SYNC':
                pass
            elif cmd == 'LIST':
                pass
            elif cmd == 'EXIT':
                print 'Disconnected from server...'
                reactor.stop()
        # send new request for server in JSON
        self.sendMessage(str(data))


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'debug':
        log.startLogging(sys.stdout)

    parser = OptionParser()
    parser.add_option("-u", "--url", dest = "url", help = "The WebSocket URL", default = "wss://localhost:9000")
    (options, args) = parser.parse_args()

    ## create a WS server factory with our protocol
    factory = WebSocketClientFactory(options.url, debug = False)
    factory.protocol = DFSClientProtocol

    ## SSL client context: using default
    if factory.isSecure:
        contextFactory = ssl.ClientContextFactory()
    else:
        contextFactory = None

    connectWS(factory, contextFactory)
    reactor.run()