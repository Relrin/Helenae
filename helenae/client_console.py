import sys

from json import dumps, loads

from optparse import OptionParser

from twisted.python import log
from twisted.internet import reactor, ssl

from autobahn.twisted.websocket import WebSocketClientFactory, WebSocketClientProtocol, connectWS

# TODO: Create plugins for future commands
# TODO: Define commands for USER (auth, read/write/sync files, etc.)
# TODO: Add methods/commands into ServerClientSSL

class DFSClientProtocol(WebSocketClientProtocol):

    def onOpen(self):
        """
            Send auth request to server, when create connection
        """
        login = raw_input('Login:')
        password = raw_input('Password:')
        hash_password = str(hash(password))
        data = dumps({'cmd': 'AUTH', 'user': login, 'password': hash_password, 'auth': False, 'error': 0})
        self.sendMessage(str(data))

    def onMessage(self, payload, isBinary):
        """
            Processing responses from server and send new requests to there
        """
        json_data = loads(payload)
        # for none-authorized users commands
        if json_data['auth'] == False:
            # error in login or password --> try again...
            if json_data['cmd'] == 'RAUT':
                print 'Error: %s' % json_data['error']
                json_data['user'] = raw_input('Login:')
                password= raw_input('Password:')
                json_data['password'] = str(hash(password))
                json_data['cmd'] = 'AUTH'
            if json_data['cmd'] == 'BBYE':
                print 'server say BYE-BYE!'
        # for authorized users commands
        else:
            print json_data


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
