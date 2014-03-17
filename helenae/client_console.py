import sys
import os
import platform
import getpass
from subprocess import Popen, PIPE, STDOUT
from json import dumps, loads, dump
from optparse import OptionParser
from hashlib import md5
from random import randint

from twisted.python import log
from twisted.internet import reactor, ssl
from autobahn.twisted.websocket import WebSocketClientFactory, WebSocketClientProtocol, connectWS

import commands

# TODO: Create plugins for future commands
# TODO: Define commands for USER (auth, read/write/sync files, etc.)
# TODO: Add methods/commands into DFSClientProtocol
# TODO: Add response after write/read/delete/etc.
# TODO: Create special folder for configs
# TODO: Crypting json values!!!

def md5_for_file(file_path, block_size=8192):
    """
        Calculating MD5 hash for file
    """
    size = 0
    md5_hash = md5()
    try:
        size = os.path.getsize(file_path)
        f = open(file_path, 'rb')
        while True:
            data = f.read(block_size)
            if not data:
                break
            md5_hash.update(data)
        f.close()
    except IOError:
        print 'ERROR: No such file or directory'
    return md5_hash.hexdigest(), size


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
        handlers['WRTE'] = self.__WRTE
        handlers['DELT'] = None
        handlers['RNME'] = None
        handlers['SYNC'] = None
        handlers['LIST'] = None
        handlers['EXIT'] = self.__EXIT
        # continues operations...
        handlers['COWF'] = self.__COWF
        # errors, bans, etc.
        handlers['CREG'] = self.__CREG
        handlers['RREG'] = self.__RREG
        handlers['RAUT'] = self.__RAUT
        return handlers

    def __SendInfoToFileServer(self, json_path, ip, port):
        p = Popen(["python", "./fileserver/fileserver_client.py", str(json_path), str(ip), str(port)], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
        result = p.communicate()[0]

    def __CREG(self):
        """
            Processing for CREG command
        """
        print "Registration has complete! Now you can connecting to DFS..."
        reactor.stop()

    def __AUTH(self, data):
        """
            Processing for AUTH command
        """
        self.counterAttemptsLogin = 3
        login, password = self.inputData()
        data = commands.constructDataClient('AUTH', login, password, False)
        return data

    def __WRTE(self, data):
        """
            Processing for WRTE (write file) command
        """
        file_path = unicode('')
        while not os.path.isfile(file_path):
            self.clear_console()
            print 'Please, enter correct path to your FILE'
            file_path = unicode(raw_input('Path:'))
        file_hash, file_size = md5_for_file(file_path)
        data = commands.constructFileDataByClient('WRTE', data['user'], data['password'], True, file_path, file_size, file_hash)
        return data

    def __COWF(self, data):
        """
            Processing for COWF command (continue operation with file)
        """
        server_ip = str(data['server'][0])
        server_port = str(data['server'][1])
        json_file = str('./fsc_' + data['user'] + '_' + str(randint(0, 100000)) + '.json')
        with open(json_file, 'w+') as f:
            dict_json = {"cmd": data['json'][0], "user": data['json'][1],
                         "file_id": data['json'][2], "src_file": data['json'][3]}
            dump(dict_json, f)
        self.__SendInfoToFileServer(json_file,server_ip,server_port)
        data['cmd'] = 'AUTH'
        del data['server']
        del data['json']

    def __EXIT(self, data):
        """
            Processing for EXIT command
        """
        print 'Disconnected from server...'
        reactor.stop()

    def __RREG(self, data):
        """
            Processing for RREG command (when error on creating new account)
        """
        print data['error']
        login, password, fullname, email = self.inputDataNewUser()
        data = dumps({'cmd': 'REGS', 'user': login, 'password': password, 'auth': False, 'error': [],
                      'email': email, 'fullname': fullname})
        return data

    def __RAUT(self, data):
        """
            Processing for RAUTH command
        """
        if self.counterAttemptsLogin > 0:
            for error in data['error']:
                print error
            print 'Attempts left: %d\n' % self.counterAttemptsLogin
            self.counterAttemptsLogin -= 1
            login, password = self.inputData()
            data = commands.constructDataClient('AUTH', login, password, False)
        else:
            print '\nTrying to hacking account or DDoS server? I will stop YOU!'
            reactor.stop()
        return data

    def clear_console(self):
        # clear console
        if platform.system() == "Linux":
            # its Linux/MacOS
            os.system('clear')
        else:
            # its Windows
            os.system('cls')

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

    def inputDataNewUser(self):
        """
            Input all data about new registered user
        """
        login = raw_input('Login:')
        password = getpass.getpass('Password:')
        fullname = raw_input('Full name:')
        email = raw_input('E-mail:')
        return login, password, fullname, email

    def onOpen(self):
        """
            Send auth request to server, when create connection
        """
        cmd = ''
        while cmd not in ('EXIT', 'REGS', 'AUTH'):
            self.clear_console()
            print "Available commands: "
            print "\tAUTH \t Authenticate user"
            print "\tREGS \t Register new user"
            print "\tEXIT \t Exit from program"
            cmd = raw_input('Command: ').upper()
        if cmd == 'REGS':
            login, password, fullname, email = self.inputDataNewUser()
            data = dumps({'cmd': 'REGS', 'user': login, 'password': password, 'auth': False, 'error': [],
                          'email': email, 'fullname': fullname})
            self.sendMessage(str(data))
        if cmd == 'AUTH':
            login, password = self.inputData()
            data = dumps({'cmd': 'AUTH', 'user': login, 'password': password, 'auth': False, 'error': []})
            self.sendMessage(str(data))
        if cmd == 'EXIT':
            reactor.stop()


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
            if data['cmd'] in ['COWF']:
                continue_cmd = data['cmd']
                self.commands_handlers[continue_cmd](data)
            self.clear_console()
            if data['error']:
                print '-----------------------======= ERRORS & WARNINGS =======-----------------------'
                for error in data['error']:
                    print error
                print '-----------------------=================================-----------------------'
            # get user a opportunity to working with server/files/etc.
            print "Current user: %s" % (data['user'])
            self.mainMenu()
            cmd = ''
            while cmd not in self.commands.keys() + ['COWF']:
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

    # create a WS server factory with our protocol
    factory = WebSocketClientFactory(options.url, debug = False)
    factory.protocol = DFSClientProtocol

    # SSL client context: using default
    if factory.isSecure:
        contextFactory = ssl.ClientContextFactory()
    else:
        contextFactory = None

    connectWS(factory, contextFactory)
    reactor.run()