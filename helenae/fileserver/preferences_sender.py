import sys
from json import dumps, loads, load

from twisted.internet import reactor, ssl
from autobahn.twisted.websocket import WebSocketClientFactory, WebSocketClientProtocol, connectWS

CONFIG_PORT = 9000
CONFIG_DATA = {}
CONFIG_TEMPLATE = ''


class PreferencesSenderProtocol(WebSocketClientProtocol):

    def onOpen(self):
        data = dumps({'cmd': 'FSRV', 'user': 'FS', 'server_port': CONFIG_PORT, 'auth': True})
        self.sendMessage(str(data))

    def onMessage(self, payload, isBinary):
        reactor.stop()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "using python fileserver_client.py [PATH_TO_config.json_FILE] [PORT_FS]"
    else:
        # read config file
        CONFIG_TEMPLATE = sys.argv[1]
        with open(CONFIG_TEMPLATE, "r") as f:
            CONFIG_DATA = load(f)
        # checking IP and PORT
        try:
            CONFIG_PORT = int(sys.argv[2])
        except ValueError:
            print 'PLEASE, enter correct information about server...'
            sys.exit(1)
        except Exception, e:
            print e
            sys.exit(1)
        server_addr = "wss://%s:%d" % (CONFIG_DATA['server_ip'], CONFIG_DATA['server_port'])
        ## create a WS server factory with our protocol
        factory = WebSocketClientFactory(server_addr, debug = False)
        factory.protocol = PreferencesSenderProtocol

        ## SSL client context: using default
        if factory.isSecure:
            contextFactory = ssl.ClientContextFactory()
        else:
            contextFactory = None

        connectWS(factory, contextFactory)
        reactor.run()