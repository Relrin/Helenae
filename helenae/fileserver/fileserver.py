import os
import sys
import json
from subprocess import Popen, PIPE, STDOUT

from twisted.internet.task import deferLater
from twisted.internet import reactor
from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol, listenWS

# TODO: Add Twisted logger
# TODO: Create plugin for fileserver (using twistd)
# TODO: Thinking about using SSL over my WebSockets message-based protocol (OR using AES algorithm?)

CONFIG_IP = 'localhost'
CONFIG_PORT = 8888
CONFIG_TEMPLATE = ''
CONFIG_DATA = {}


def sendPrefences(port):
    p = Popen(["python", "preferences_sender.py", str(CONFIG_TEMPLATE), str(port)], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    result = p.communicate()[0]



class MessageBasedServerProtocol(WebSocketServerProtocol):
    """
        Message-based WebSockets server
        Template contains some parts as string:
        [USER_ID:OPERATION_NAME:FILE_ID] -  15 symbols for USER_ID,
                                            10 symbols for OPERATION_NAME,
                                            25 symbols for FILE_ID
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
            os.makedir(path)
            os.chdir(path)
            os.mkdir(base_dir)
            os.chdir(base_dir)
        # init some things
        self.fullpath = path + '/' + base_dir
        self.status = 'ONLINE'

    def __checkUserCatalog(self, user_id):
        # prepare to working with files...
        os.chdir(self.fullpath)
        if not os.path.exists(user_id) or not os.path.isdir(user_id):
            os.mkdir(user_id)
            os.chdir(user_id)
        else:
            os.chdir(self.fullpath + '/' + user_id)

    def onOpen(self):
        print "[USER] User with %s connected" % (self.transport.getPeer())

    def connectionLost(self, reason):
        print '[USER] Lost connection from %s' % (self.transport.getPeer())

    def onMessage(self, payload, isBinary):
        """
            Processing request from user and send response
        """
        user_id, cmd, file_id = payload[:54].replace('[', '').replace(']','').split(':')
        data = payload[54:]
        operation = "UNK"  # WRT -> Write, REA -> Read, DEL -> Delete, STS -> Status, UNK -> Unknown
        status = "C"       # C -> Complete, E -> Error in operation
        commentary = 'Succesfull!'
        # write file into user storage
        if cmd == 'WRITE_FILE':
            self.status = 'BUSY'
            self.__checkUserCatalog(user_id)
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
        # read some file
        elif cmd == 'READU_FILE':
            self.status = 'BUSY'
            self.__checkUserCatalog(user_id)
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
        # delete file from storage (and in main server, in parallel delete from DB)
        elif cmd == 'DELET_FILE':
            self.status = 'BUSY'
            self.__checkUserCatalog(user_id)
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
        elif cmd == 'STATUS_SRV':
            operation = "STS"
            commentary = self.status
        self.sendMessage('[%s][%s]%s' % (operation, status, commentary), isBinary=True)


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
        d = deferLater(reactor, 0, sendPrefences, CONFIG_PORT)
        reactor.run()