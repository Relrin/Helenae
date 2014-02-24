import sys
import os
import platform
import getpass
from json import dumps, loads
from optparse import OptionParser

from twisted.python import log
from twisted.internet import reactor, ssl
from autobahn.twisted.websocket import WebSocketClientFactory, WebSocketClientProtocol, connectWS

import commands

# TODO: Create plugins for future commands
# TODO: Define commands for USER (auth, read/write/sync files, etc.)
# TODO: Add methods/commands into ServerClientSSL


class DFSClientProtocol(WebSocketClientProtocol):

    commands = commands.commands_user

    def __init__(self):
        self.counterAttemptsLogin = 3
        self.commands_handlers = self.__initHandlersUser()

    def __initHandlersUser(self):
        """
            Initialize handlers for every response from server
        """
        handlers = commands.commands_handlers_user
        # basic commands
        handlers['AUTH'] = self.__AUTH
        handlers['READ'] = None
        handlers['WRTE'] = None
        handlers['DELT'] = None
        handlers['RNME'] = None
        handlers['SYNC'] = None
        handlers['LIST'] = None
        handlers['EXIT'] = self.__EXIT
        # errors, bans, etc.
        handlers['RAUT'] = self.__RAUT
        handlers['BANN'] = None
        return handlers

    def __AUTH(self, data):
        """
            Processing for AUTH command
        """
        self.counterAttemptsLogin = 3
        login, password = self.inputData()
        data = commands.constructDataClient('AUTH', login, password, False)
        return data

    def __EXIT(self, data):
        """
            Processing for EXIT command
        """
        print 'Disconnected from server...'
        reactor.stop()

    def __RAUT(self, data):
        """
            Processing for RAUTH command
        """
        if self.counterAttemptsLogin > 0:
            print '\nError: %s' % data['error']
            print 'Attempts left: %d\n' % self.counterAttemptsLogin
            self.counterAttemptsLogin -= 1
            login, password = self.inputData()
            data = commands.constructDataClient('AUTH', login, password, False)
        else:
            print '\nTrying to hacking account or DDoS server? I will stop YOU!'
            reactor.stop()
        return data

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
        password = getpass.getpass('Password:')
        return login, password

    def onOpen(self):
        """
            Send auth request to server, when create connection
        """
        login, password = self.inputData()
        data = dumps({'cmd': 'AUTH', 'user': login, 'password': password, 'auth': False, 'error': ''})
        self.sendMessage(str(data))

    def onMessage(self, payload, isBinary):
        """
            Processing responses from server and send new requests to there
        """
        data = loads(payload)
        # for none-authorized users commands
        if data['auth'] == False:
            cmd = data['cmd']
            # not realized function? --> try enter next command and print error
            if (self.commands_handlers[cmd] is None):
                print '%s command is not already realized...' % cmd
            else:
                # fetch and execute command
                data = self.commands_handlers[cmd](data)
        # for authorized users commands
        else:
            # clear console at show main menu
            if platform.system() == "Linux":
                # its Linux/MacOS
                os.system('clear')
            else:
                # its Windows
                os.system('cls')
            # get user a opportunity to working with server/files/etc.
            self.mainMenu()
            cmd = ''
            while cmd not in self.commands.keys():
                cmd = raw_input('Command: ').upper()
                # not realized function? --> try enter next command and print error
                if (cmd not in self.commands.keys() or (self.commands_handlers[cmd] is None)):
                    print '%s command is not already realized...' % cmd
                    cmd = ''
            # fetch and execute command
            data = self.commands_handlers[cmd](data)
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