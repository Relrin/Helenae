import json
import sys
import os
from ast import literal_eval

from twisted.internet import reactor
from autobahn.twisted.websocket import WebSocketClientFactory, WebSocketClientProtocol, connectWS

from utils import rsync

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
        self.file_1 = None  # patched file
        self.file_2 = None  # file after receiving `delta`
        self.delta_sync = None # changes in files as delta
        self.result_cmd = ""
        self.commands_handlers = self.__initHandlersUser()
        user_id = CONFIG_DATA['user']
        operation_name = CONFIG_DATA['cmd']
        file_id = CONFIG_DATA['file_id']
        src_file = CONFIG_DATA['src_file']
        data = '[' + str(user_id) + ':' + str(operation_name) + ':' + str(file_id) + ']'
        # get data for write operations
        if operation_name == 'WRITE_FILE':
            with open(src_file, "r") as f:
                info = f.read()
            data += str(info)
        # or try to get information for sync operations
        elif operation_name == 'RSYNC_FILE':
            self.file_1 = open(src_file, "rb")
            hashes = rsync.blockchecksums(self.file_1)
            data += str(hashes)
        self.sendMessage(data, isBinary=True)

    def __initHandlersUser(self):
        handlers = {}
        handlers['WRT'] = self.print_payload
        handlers['DEL'] = self.print_payload
        handlers['REA'] = self.read_command
        handlers['RSY'] = self.read_sync
        handlers['WSY'] = self.write_sync
        handlers['SYC'] = self.print_payload
        return handlers

    def stop_and_delete_config(self):
        os.remove(CONFIG_TEMPLATE)
        reactor.stop()

    def print_payload(self, payload):
        print payload
        self.stop_and_delete_config()

    def read_command(self, payload):
        if self.result_cmd == 'C':
            try:
                data = payload[8:]
                f = open(CONFIG_DATA['src_file'], "wb")
                f.write(data)
            except IOError, e:
                print e
            except Exception, e:
                raise Exception(e)
            finally:
                print payload[:8] + "Successfully!"
                f.close()
        else:
            self.print_payload(payload)
        self.stop_and_delete_config()

    def read_sync(self, payload):
        self.delta_sync = literal_eval(payload[8:])
        self.file_1.seek(0)
        path_parts = CONFIG_DATA['src_file'].split('/')
        path_parts[-1] = 'swap-' + path_parts[-1]
        full_swap_filepath = '/'.join(path_parts)
        self.file_2 = open(full_swap_filepath, "wb")
        rsync.patchstream(self.file_1, self.file_2, self.delta_sync)
        self.file_1.close()
        self.file_2.close()
        os.remove(CONFIG_DATA['src_file'])
        os.rename(full_swap_filepath, CONFIG_DATA['src_file'])
        self.file_1 = self.file_2 = self.delta_sync = None
        self.stop_and_delete_config()

    def write_sync(self, payload):
        hashes = literal_eval(payload[8:])
        data = '[' + str(CONFIG_DATA['user']) + ':' + "WCSYN_FILE" + ':' + str(CONFIG_DATA['file_id']) + ']'
        try:
            patchedfile = open(CONFIG_DATA['src_file'], "rb")
            data += str(rsync.rsyncdelta(patchedfile, hashes))
        except IOError, argument:
            print argument.message
        except Exception, argument:
            print argument.message
            raise Exception(argument)
        self.sendMessage(data, isBinary=True)

    def onMessage(self, payload, isBinary):
        cmd = payload[1:4]
        self.result_cmd = payload[6]
        if cmd in ('WRT', 'REA', 'DEL', 'RSY', 'WSY', 'SYC'):
            self.commands_handlers[cmd](payload)


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print "using python fileserver_client.py [PATH_TO_config.json_FILE] [IP] [PORT]"
    else:
        try:
            CONFIG_TEMPLATE = sys.argv[1]
            with open(CONFIG_TEMPLATE, "r") as f:
                CONFIG_DATA = json.load(f)
            CONFIG_IP = sys.argv[2]
            CONFIG_PORT = int(sys.argv[3])
        except ValueError:
            print 'PLEASE, enter correct information about server...'
            sys.exit(1)
        except Exception, e:
            print e
            sys.exit(1)
        server_addr = "ws://%s:%d" % (CONFIG_IP, CONFIG_PORT)
        # connection to server
        factory = WebSocketClientFactory(server_addr)
        factory.protocol = MessageBasedClientProtocol
        connectWS(factory)
        reactor.run()