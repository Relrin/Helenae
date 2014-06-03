import sys
import os
import platform
import getpass
import pickle
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
        self.__filenumber = None
        self.__servers = None
        self.__files = None
        self.__user_ids = None

    def __initCashe(self, servers, files, user_ids):
        self.__servers = servers
        self.__files = files
        self.__user_ids = user_ids

    def __clearCashe(self):
        self.__servers = None
        self.__files = None
        self.__user_ids = None

    def __initHandlersUser(self):
        """
            Initialize handlers for every response from server
        """
        handlers = commands.commands_handlers_user
        # basic commands
        handlers['AUTH'] = self.__AUTH
        handlers['READ'] = self.__READ
        handlers['WRTE'] = self.__WRTE
        handlers['DELT'] = self.__DELT
        handlers['RNME'] = self.__RNME
        handlers['SYNC'] = self.__SYNC
        handlers['LIST'] = self.__LIST
        handlers['EXIT'] = self.__EXIT
        # continues operations...
        handlers['COWF'] = self.__COWF
        handlers['CLST'] = self.__CLST
        handlers['CREA'] = self.__CREA
        handlers['CDLT'] = self.__CDLT
        handlers['CRNM'] = self.__CRNM
        handlers['CSYN'] = self.__CSYN
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
        self.__clearCashe()
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
        data = commands.constructDataClient('WRTE', data['user'], data['password'], True,
                                            file_path=file_path, file_size=file_size, file_hash=file_hash)
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
        self.__clearCashe()
        data['cmd'] = 'AUTH'
        del data['server']
        del data['json']

    def __LIST(self, data):
        """
            Processing for LIST command
        """
        data = commands.constructDataClient('LIST', data['user'], data['password'], True)
        self.__clearCashe()
        return data

    def __CLST(self, data):
        """
            Processing for CLST command
        """
        files = pickle.loads(data['files'])
        servers = pickle.loads(data['servers'])
        user_id = data['user_ids']
        if files is None:
            print "WARNING: You don't write any file into storage..."
        else:
            self.__initCashe(servers, files, user_id)
            self.print_storage_files()
        data['cmd'] = 'AUTH'
        del data['files']
        del data['servers']
        del data['user_ids']

    def __READ(self, data):
        """
            Processing for READ command (read some file from FS)
        """
        if self.__files is None:
            data = commands.constructDataClient('AUTH', data['user'], data['password'], True,
                                                "WARNING: Please, use LIST to get last cashe of your files from server...")
        else:
            self.__filenumber = ''
            lst_file_numbers = [str(number+1) for number, file_fs in enumerate(self.__files)]
            while self.__filenumber not in lst_file_numbers:
                self.clear_console()
                self.print_storage_files()
                self.__filenumber = self.inputFileNumber()
            self.__filenumber = int(self.__filenumber) - 1
            file_hash = self.__files[self.__filenumber].file_hash
            data = commands.constructDataClient('READ', data['user'], data['password'], True,
                                                file_path='', file_size=0, file_hash=file_hash)
        return data

    def __CREA(self, data):
        """
            Second part of READ command: after get file list, we are read enter file name
        """
        if self.__files is None:
            print "WARNING: You don't write any file into storage..."
        else:
            # creating JSON for read operation
            server_ip = str(self.__servers[self.__filenumber][0].ip)
            server_port = str(self.__servers[self.__filenumber][0].port)
            user_id = 'u' + str(self.__user_ids).rjust(14, '0')
            file_id = str(self.__files[self.__filenumber].server_name)
            # get path to file, which using for write block readed information
            file_path = ''
            file_format_db = file_id.split('.')[-1]
            # checking entered path by user
            while file_path == '':
                self.clear_console()
                print 'NOTE: file shall be have equals format!'
                print 'Enter path to file, which using to store information:'
                file_path = raw_input('Path:')
                file_format = file_path.split('/')[-1].split('.')[-1]
                if len(file_format[0]) == 0:
                    file_path = ''
                if file_format != file_format_db:
                    file_path = ''
                if os.path.exists(file_path):
                    file_path = ''
            json_file = str('./fsc_' + data['user'] + '_' + str(randint(0, 100000)) + '.json')
            with open(json_file, 'w+') as f:
                dict_json = {"cmd": "READU_FILE", "user": user_id,
                             "file_id": file_id, "src_file": file_path}
                dump(dict_json, f)
            # stating second subprocess
            self.__SendInfoToFileServer(json_file, server_ip, server_port)
        self.__filenumber = None
        data['cmd'] = 'AUTH'

    def __DELT(self, data):
        """
            Processing for DELT command
        """
        if self.__files is None:
            data = commands.constructDataClient('AUTH', data['user'], data['password'], True,
                                                "WARNING: Please, use LIST to get last cashe of your files from server...")
        else:
            self.__filenumber = ''
            lst_file_numbers = [str(number+1) for number, file_fs in enumerate(self.__files)]
            while self.__filenumber not in lst_file_numbers:
                self.clear_console()
                self.print_storage_files()
                self.__filenumber = self.inputFileNumber()
            self.__filenumber = int(self.__filenumber) - 1
            file_id = self.__files[self.__filenumber].id
            file_hash = self.__files[self.__filenumber].file_hash
            data = commands.constructDataClient('DELT', data['user'], data['password'], True,
                                                file_path=file_id, file_size=0, file_hash=file_hash)
        return data

    def __CDLT(self, data):
        """
            Sending to server command to delete some file from user storage
        """
        if self.__files is None:
            print "WARNING: You don't write any file into storage..."
        else:
            # creating JSON for read operation
            server_ip = str(self.__servers[self.__filenumber][0].ip)
            server_port = str(self.__servers[self.__filenumber][0].port)
            user_id = 'u' + str(self.__user_ids).rjust(14, '0')
            file_id = str(self.__files[self.__filenumber].server_name)
            # checking entered path by user
            json_file = str('./fsc_' + data['user'] + '_' + str(randint(0, 100000)) + '.json')
            with open(json_file, 'w+') as f:
                dict_json = {"cmd": "DELET_FILE", "user": user_id,
                             "file_id": file_id, "src_file": ''}
                dump(dict_json, f)
            # stating second subprocess
            self.__SendInfoToFileServer(json_file, server_ip, server_port)
        self.__filenumber = None
        self.__clearCashe()
        data['cmd'] = 'AUTH'

    def __RNME(self, data):
        """
            Rename file handler for RNME operation
        """
        if self.__files is None:
            data = commands.constructDataClient('AUTH', data['user'], data['password'], True,
                                                "WARNING: Please, use LIST to get last cashe of your files from server...")
        else:
            self.__filenumber = ''
            lst_file_numbers = [str(number+1) for number, file_fs in enumerate(self.__files)]
            while self.__filenumber not in lst_file_numbers:
                self.clear_console()
                self.print_storage_files()
                self.__filenumber = self.inputFileNumber()
            self.__filenumber = int(self.__filenumber) - 1
            # get file info (id and original name)
            file_id = self.__files[self.__filenumber].id
            file_original_name = self.__files[self.__filenumber].original_name
            file_format_db = file_original_name.split('.')[-1]
            new_name = ''
            # checking entered path by user
            while new_name == '':
                self.clear_console()
                print 'NOTE: file shall be have equals format!'
                print 'Enter new name for file, which replaced previous name:'
                new_name = raw_input('New name:')
                file_format = new_name.split('/')[-1].split('.')[-1]
                if len(file_format[0]) == 0:
                    new_name = ''
                if file_format != file_format_db:
                     new_name = ''
            data = commands.constructDataClient('RNME', data['user'], data['password'], True,
                                                file_id=file_id, new_name=new_name)
        return data

    def __CRNM(self, data):
        print 'Rename has complete!'
        print 'Please, use LIST command for get last state of cashe...'
        self.__clearCashe()
        data['cmd'] = 'AUTH'

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
        for error in data['error']:
            print error
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

    def __SYNC(self, data):
        """
            Processing for SYNC command
        """
        if self.__files is None:
            data = commands.constructDataClient('AUTH', data['user'], data['password'], True,
                                                "WARNING: Please, use LIST to get last cashe of your files from server...")
        else:
            self.__filenumber = ''
            lst_file_numbers = [str(number+1) for number, file_fs in enumerate(self.__files)]
            while self.__filenumber not in lst_file_numbers:
                self.clear_console()
                self.print_storage_files()
                self.__filenumber = self.inputFileNumber()
            self.__filenumber = int(self.__filenumber) - 1
            files = [(self.__files[self.__filenumber].original_name, self.__files[self.__filenumber].server_name,
                      self.__files[self.__filenumber].file_hash)]
            data = commands.constructDataClient('SYNC', data['user'], data['password'], True, files_u=files)
            print data
        return data

    def __CSYN(self, data):
        """
            Continues SYNC operation
            NOT COMPLETED!
            create connection to server with rsync module and get updates...
        """
        print data

    def clear_console(self):
        # clear console
        if platform.system() == "Linux":
            # its Linux/MacOS
            os.system('clear')
        else:
            # its Windows
            os.system('cls')

    def print_storage_files(self):
        """
            Display all files, which user loaded on server
        """
        print "--------------------------------"
        print "Files:"
        for (id_enum, file_storage) in enumerate(self.__files):
            file_size = commands.convertSize(file_storage.chunk_size)
            print "%d. %s\t[Size: %s]" % (id_enum + 1, file_storage.original_name, str(file_size))
        print "--------------------------------"

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

    def inputFileNumber(self):
        """
            Input file number after getting print all file list
        """
        filenumber = ''
        try:
            filenumber = raw_input('File number:')
        except ValueError:
            print 'Enter only DIGITS, which equals some file, not text!'
        return filenumber

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
        if data['auth'] is False:
            cmd = data['cmd']
            # not realized function? --> try enter next command and print error
            if (self.commands_handlers[cmd] is None):
                print '%s command is not already realized...' % cmd
            else:
                # fetch and execute command
                data = self.commands_handlers[cmd](data)
        # for authorized users commands
        else:
            self.clear_console()
            if data['cmd'] in ['COWF', 'CLST', 'CREA', 'CDLT', 'CRNM', 'CSYN']:
                continue_cmd = data['cmd']
                self.commands_handlers[continue_cmd](data)
            if data['error']:
                print '-----------------------======= ERRORS & WARNINGS =======-----------------------'
                for error in data['error']:
                    print error
                print '-----------------------=================================-----------------------'
            # get user a opportunity to working with server/files/etc.
            print "Current user: %s" % (data['user'])
            self.mainMenu()
            cmd = ''
            while cmd not in self.commands.keys() + ['COWF', 'CLST', 'CREA', 'CDLT', 'CRNM', 'CSYN']:
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
    parser.add_option("-i", "--ip", dest = "ip", help = "The WebSocket IP", default = "localhost")
    parser.add_option("-p", "--port", dest = "port", help = "The WebSocket port", default = "9000")
    (options, args) = parser.parse_args()

    host_url = "wss://%s:%s" % (options.ip, options.port)
    # create a WS server factory with our protocol
    factory = WebSocketClientFactory(host_url, debug = False)
    factory.protocol = DFSClientProtocol

    # SSL client context: using default
    if factory.isSecure:
        contextFactory = ssl.ClientContextFactory()
    else:
        contextFactory = None

    connectWS(factory, contextFactory)
    reactor.run()
