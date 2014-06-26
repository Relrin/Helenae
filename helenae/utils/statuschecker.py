import sys

from twisted.internet.task import deferLater
from twisted.internet import reactor
from autobahn.twisted.websocket import WebSocketClientFactory, WebSocketClientProtocol, connectWS

CONFIG_IP = 'localhost'
CONFIG_PORT = 9000


def isOffline(status):
    print '%s|%d|%s' % (CONFIG_IP, CONFIG_PORT, status)


class StatusCheckerProtocol(WebSocketClientProtocol):

    def __init__(self):
        self.operation_name = "STATUS_SRV"
        self.user_id = 'u00000000000000'
        self.file_id = "000000000000000000000.log"

    def onOpen(self):
        data = '[' + str(self.user_id) + ':' + str(self.operation_name) + ':' + str(self.file_id) + ']'
        self.sendMessage(data, isBinary=True)

    def onMessage(self, payload, isBinary):
        cmd = payload[1:4]
        result_cmd = payload[6]
        data = payload[8:]
        print '%s|%d|%s' % (CONFIG_IP, CONFIG_PORT, data)
        reactor.stop()


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "using python statuschecker.py [IP] [PORT]"
    else:
        try:
            # read preferences
            CONFIG_IP = sys.argv[1]
            CONFIG_PORT = int(sys.argv[2])
        except ValueError:
            print 'PLEASE, enter correct information about server...'
            sys.exit(1)
        except Exception, e:
            print e
            sys.exit(1)
        server_addr = "ws://%s:%d" % (CONFIG_IP, CONFIG_PORT)
        # connection to server
        factory = WebSocketClientFactory(server_addr)
        factory.protocol = StatusCheckerProtocol
        connectWS(factory)
        # create special Deffered, which disconnect us from some server, if can't connect within 3 seconds
        d = deferLater(reactor, 3, isOffline, 'OFFLINE')
        d.addCallback(lambda ignored: reactor.stop())
        # run all system...
        reactor.run()