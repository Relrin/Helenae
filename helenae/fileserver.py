import os
import sys
import json
from subprocess import Popen, PIPE, STDOUT

from twisted.internet.task import deferLater
from twisted.internet import reactor
from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol, listenWS

from utils import rsync

# TODO: Add Twisted logger
# TODO: Create plugin for fileserver (using twistd)
# TODO: Thinking about using SSL over my WebSockets message-based protocol (OR using AES algorithm?)

CONFIG_IP = 'localhost'
CONFIG_PORT = 8888
CONFIG_TEMPLATE = ''
CONFIG_DATA = {}
BATCH_SIZE = 1 * 2 ** 20


def sendPrefences(port):
    p = Popen(["python", "./utils/preferences_sender.py", str(CONFIG_TEMPLATE), str(port)], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    result = p.communicate()[0]


class MessageBasedServerProtocol(WebSocketServerProtocol):
    """
        Message-based WebSockets server
        Template contains some parts as string:
        [USER_ID:OPERATION_NAME:FILE_ID:FILE_ENC_PASSWORD] - 15 symbols for USER_ID,
                                                             10 symbols for OPERATION_NAME,
                                                             25 symbols for FILE_ID
                                                             32 symbols for FILE_ENC_PASSWORD
        other - some data
    """

    def __init__(self):
        path = CONFIG_DATA['path']
        base_dir = CONFIG_DATA['base_dir']
        # prepare to working with files...
        if os.path.exists(path) and os.path.isdir(path):
            os.chdir(path)
            if not os.path.exists(base_dir) or not os.path.isdir(base_dir):
                os.mkdir(base_dir)
                os.chdir(base_dir)
        else:
            os.mkdir(path)
            os.chdir(path)
            os.mkdir(base_dir)
            os.chdir(base_dir)
        # init some things
        self.fullpath = path + '/' + base_dir
        self.status = 'ONLINE'
        self.commands_handlers = self.__initHandlersUser()
        self.file_1 = self.file_2 = self.delta_sync = None
        self.file_enc_psw = None

    def __initHandlersUser(self):
        """
            Initialize handlers for every command
        """
        handlers = {}
        handlers['WRITE_FILE'] = self.write_file
        handlers['READU_FILE'] = self.read_file
        handlers['DELET_FILE'] = self.delete_file
        handlers['STATUS_SRV'] = self.status_server
        handlers['RSYNC_FILE'] = self.rsync_file
        handlers['WSYNC_FILE'] = self.wsync_file
        return handlers

    def __checkUserCatalog(self, user_id):
        # prepare to working with files...
        os.chdir(self.fullpath)
        if not os.path.exists(user_id) or not os.path.isdir(user_id):
            os.mkdir(user_id)
            os.chdir(user_id)
        else:
            os.chdir(self.fullpath + '/' + user_id)

    def __get_standart_states(self):
        return "C", 'Succesfull!'

    def write_file(self, user_id, file_id, data):
        print "[USER] User with %s was write a file..." % (self.transport.getPeer())
        status, commentary = self.__get_standart_states()
        self.__checkUserCatalog(user_id)
        self.status = 'BUSY'
        operation = "WRT"
        try:
            f = open(file_id, "wb")
            f.write(data)
        except IOError, argument:
            status = "E"
            commentary = argument
        except Exception, argument:
            status = "E"
            commentary = argument
            raise Exception(argument)
        finally:
            f.close()
        self.status = 'ONLINE'
        return operation, status, commentary

    def read_file(self, user_id, file_id, data):
        print "[USER] User with %s was read a file..." % (self.transport.getPeer())
        status, commentary = self.__get_standart_states()
        self.__checkUserCatalog(user_id)
        self.status = 'BUSY'
        operation = "REA"
        try:
            f = open(file_id, "rb")
            commentary = f.read()
        except IOError, argument:
            status = "E"
            commentary = argument
        except Exception, argument:
            status = "E"
            commentary = argument
            raise Exception(argument)
        finally:
            f.close()
        self.status = 'ONLINE'
        return operation, status, commentary

    def delete_file(self, user_id, file_id, data):
        print "[USER] User with %s was delete a file..." % (self.transport.getPeer())
        status, commentary = self.__get_standart_states()
        self.__checkUserCatalog(user_id)
        self.status = 'BUSY'
        operation = "DEL"
        try:
            os.remove(file_id)
        except IOError, argument:
            status = "E"
            commentary = argument
        except Exception, argument:
            status = "E"
            commentary = argument
            raise Exception(argument)
        self.status = 'ONLINE'
        return operation, status, commentary

    def rsync_file(self, user_id, file_id, data):
        print "[USER] User with %s sync files..." % (self.transport.getPeer())
        status, commentary = self.__get_standart_states()
        self.__checkUserCatalog(user_id)
        self.status = 'BUSY'
        operation = "RSY"
        try:
            f = open(file_id, "rb")
            commentary = f.read()
        except IOError, argument:
            status = "E"
            commentary = argument
        except Exception, argument:
            status = "E"
            commentary = argument
            raise Exception(argument)
        self.status = 'ONLINE'
        return operation, status, commentary

    def wsync_file(self, user_id, file_id, data):
        print "[USER] User with %s sync files..." % (self.transport.getPeer())
        status, commentary = self.__get_standart_states()
        self.__checkUserCatalog(user_id)
        self.status = 'BUSY'
        operation = "WRT"
        try:
            unpatched = open(file_id, "rb")
            hashes = rsync.blockchecksums(unpatched)

            new_file = file_id + '.new'
            swap_path = file_id + '~'
            with open(swap_path, "wb") as out_file:
                out_file.write(data)

            patchedfile = open(swap_path, "rb")
            delta = rsync.rsyncdelta(patchedfile, hashes)

            unpatched.seek(0)
            save_to = open(new_file, "wb")
            rsync.patchstream(unpatched, save_to, delta)

            save_to.close()
            patchedfile.close()
            unpatched.close()

            if os.path.exists(file_id):
                os.remove(file_id)

            os.rename(new_file, file_id)

            if os.path.exists(swap_path):
                os.remove(swap_path)
        except IOError, argument:
            status = "E"
            commentary = argument
        except Exception, argument:
            status = "E"
            commentary = argument
            raise Exception(argument)
        finally:
            print 'WSYNC was ended successfully!'
        self.status = 'ONLINE'
        return operation, status, commentary

    def status_server(self, user_id, file_id, data):
        print "[SERV] Server with %s getting fileserver status..." % (self.transport.getPeer())
        status = "C"
        operation = "STS"
        commentary = self.status
        return operation, status, commentary

    def onOpen(self):
        print "[USER] User with %s connected" % (self.transport.getPeer())

    def connectionLost(self, reason):
        print '[USER] Lost connection from %s' % (self.transport.getPeer())

    def onMessage(self, payload, isBinary):
        """
            Processing request from user and send response
        """
        user_id, cmd, file_id, self.file_enc_psw = payload[:87].replace('[', '').replace(']', '').split(':')
        self.file_enc_psw = self.file_enc_psw.replace('~', '')
        data = payload[86:]
        operation, status, commentary = "UNK", "C", "Successfull!"
        if cmd in ('WRITE_FILE', 'READU_FILE', 'DELET_FILE', 'STATUS_SRV', 'RSYNC_FILE', 'WSYNC_FILE'):
            operation, status, commentary = self.commands_handlers[cmd](user_id, file_id, data)
        self.file_enc_psw = None
        self.sendMessage('[%s][%s]%s' % (operation, status, commentary), isBinary=True, sync=True)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "using python fileserver_client.py [PATH_TO_config.json_FILE] [PORT]"
    else:
        try:
            # read config file
            CONFIG_TEMPLATE = sys.argv[1]
            with open(CONFIG_TEMPLATE, "r") as f:
                CONFIG_DATA = json.load(f)
            # checking IP and PORT
            CONFIG_PORT = int(sys.argv[2])
        except ValueError:
            print 'PLEASE, enter correct information about server...'
            sys.exit(1)
        except Exception, e:
            print e
            sys.exit(1)
        if CONFIG_IP == 'localhost':
            CONFIG_IP = '127.0.0.1'
        server_addr = "ws://%s:%d" % (CONFIG_IP, CONFIG_PORT)
        # create server
        factory = WebSocketServerFactory(server_addr)
        factory.protocol = MessageBasedServerProtocol
        listenWS(factory)
        # create special Deffered, which sending our server prefences (ip and port) to main server
        if bool(CONFIG_DATA["debug"]) is False:
            d = deferLater(reactor, 0, sendPrefences, CONFIG_PORT)
        reactor.run()
