import json
import sys
import commands

from twisted.internet import reactor
from autobahn.twisted.websocket import WebSocketClientFactory, WebSocketClientProtocol, connectWS

CONFIG_TEMPLATE = ''
CONFIG_DATA = {}


class MessageBasedClientProtocol(WebSocketClientProtocol):
    """
        Message-based WebSockets client
        Template contains some parts as string:
            [USER_ID:OPERATION_NAME:FILE_ID] -  15 symbols for USER_ID,
                                                10 symbols for OPERATION_NAME,
                                                25 symbols for FILE_ID
            other - some data
    """
    def onOpen(self):
        user_id = CONFIG_DATA['user']
        operation_name = CONFIG_DATA['cmd']
        file_id = CONFIG_DATA['file_id']
        src_file = CONFIG_DATA['src_file']
        with open(src_file, "r") as f:
            info = f.read()
        data = '[' + str(user_id) + ':' + str(operation_name) + ':' + str(file_id) + ']' + str(info)
        self.sendMessage(data, isBinary=True)

    def onMessage(self, payload, isBinary):
        print payload
        reactor.stop()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "using python fileserver_client.py [PATH_TO_config.json_FILE]"
    else:
        # read config file
        CONFIG_TEMPLATE = sys.argv[1]
        with open(CONFIG_TEMPLATE, "r") as f:
            CONFIG_DATA = json.load(f)
        # connection to server
        factory = WebSocketClientFactory("ws://localhost:9000")
        factory.protocol = MessageBasedClientProtocol
        connectWS(factory)
        reactor.run()