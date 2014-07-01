import json
import sys
import os

from twisted.internet import reactor
from autobahn.twisted.websocket import WebSocketClientFactory, WebSocketClientProtocol, connectWS

from utils import rsync
from utils.crypto import aes

CONFIG_TEMPLATE = ''
CONFIG_DATA = {}
CONFIG_PASSWORD = ''


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
        data = '[' + str(user_id) + ':' + str(operation_name) + ':' + str(file_id) + ':' + str(CONFIG_PASSWORD) + ']'
        # get data for write operations
        if operation_name in ('WRITE_FILE', 'WSYNC_FILE'):
            with open(src_file, "rb") as in_file:
                for chunk in aes.encrypt(in_file, str(CONFIG_PASSWORD), key_length=32):
                    data += chunk
        self.sendMessage(data, isBinary=True, sync=True)

    def __initHandlersUser(self):
        handlers = {}
        handlers['WRT'] = self.print_payload
        handlers['DEL'] = self.print_payload
        handlers['REA'] = self.read_command
        handlers['RSY'] = self.rsync_file
        handlers['WSY'] = self.print_payload
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
                text = payload[8:]
                with open(CONFIG_DATA['src_file'], 'wb') as out_file:
                    for chunk in aes.decrypt(text, str(CONFIG_PASSWORD), key_length=32):
                        out_file.write(chunk)
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

    def rsync_file(self, payload):
        if self.result_cmd == 'C':
            try:
                unpatched = open(CONFIG_DATA['src_file'], "rb")
                hashes = rsync.blockchecksums(unpatched)

                new_file = CONFIG_DATA['src_file'] + '.new'
                swap_path = CONFIG_DATA['src_file'] + '~'
                text = payload[8:]
                with open(swap_path, 'wb') as out_file:
                    for chunk in aes.decrypt(text, str(CONFIG_PASSWORD), key_length=32):
                        out_file.write(chunk)

                patchedfile = open(swap_path, "rb")
                delta = rsync.rsyncdelta(patchedfile, hashes)

                unpatched.seek(0)
                save_to = open(new_file, "wb")
                rsync.patchstream(unpatched, save_to, delta)

                save_to.close()
                patchedfile.close()
                unpatched.close()

                if os.path.exists(CONFIG_DATA['src_file']):
                    os.remove(CONFIG_DATA['src_file'])

                os.rename(new_file, CONFIG_DATA['src_file'])

                if os.path.exists(swap_path):
                    os.remove(swap_path)
            except IOError, e:
                print e
            except Exception, e:
                raise Exception(e)
            finally:
                print payload[:8] + "Successfully!"
        else:
            self.print_payload(payload)
        self.stop_and_delete_config()

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
            CONFIG_PASSWORD = CONFIG_DATA['password']
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