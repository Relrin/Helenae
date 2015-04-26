import json
import sys
import os

from twisted.internet import reactor
from autobahn.twisted.websocket import WebSocketClientFactory, WebSocketClientProtocol, connectWS

from utils import rsync
from utils.crypto.aes import AES_wrapper

CONFIG_TEMPLATE = ''
CONFIG_DATA = {}
CONFIG_PASSWORD = ''


class MessageBasedClientProtocol(WebSocketClientProtocol):
    """
        Message-based WebSockets client
        Template contains some parts as string:
            [USER_ID:OPERATION_NAME:FILE_ID:PSW_KEY] -  15 symbols for USER_ID,
                                                        10 symbols for OPERATION_NAME,
                                                        25 symbols for FILE_ID,
                                                        32 symbols for PSW_KEY
            other - some data
    """
    def onOpen(self):
        self.file_1 = None  # patched file
        self.file_2 = None  # file after receiving `delta`
        self.delta_sync = None # changes in files as delta
        self.result_cmd = ""
        self.commands_handlers = self.__initHandlersUser()
        self.crypto_classes = self.__initCryptoHandlers()
        user_id = CONFIG_DATA['user']
        operation_name = CONFIG_DATA['cmd']
        file_id = CONFIG_DATA['file_id']
        src_file = CONFIG_DATA['src_file']
        self.algorithm = CONFIG_DATA['algorithm']
        data = '[' + str(user_id) + ':' + str(operation_name) + ':' + str(file_id) + ':' + str(CONFIG_PASSWORD) + ']'
        # get data for write operations
        if operation_name in ('WRITE_FILE', 'WSYNC_FILE'):
            crypto_object = self.getCryptoObject()
            with open(src_file, "rb") as in_file:
                for chunk in crypto_object.encrypt(in_file, str(CONFIG_PASSWORD), key_length=32):
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

    def __initCryptoHandlers(self):
        # TODO: Add there Twofish and Serpent wrappers
        handlers = {}
        handlers['AES-256'] = AES_wrapper
        handlers['Twofish'] = None
        handlers['Serpent'] = None
        return handlers

    def getCryptoObject(self):
        if self.algorithm not in self.crypto_classes.keys():
            raise NotImplementedError('Algorithm {} not implemented!'.format(self.algorithm))
        return self.crypto_classes[self.algorithm]()

    def stop_and_delete_config(self):
        os.remove(CONFIG_TEMPLATE)
        reactor.stop()

    def print_payload(self, payload):
        print payload
        self.stop_and_delete_config()

    def read_command(self, payload):
        if self.result_cmd == 'C':
            try:
                crypto_object = self.getCryptoObject()
                text = payload[8:]
                with open(CONFIG_DATA['src_file'], 'wb') as out_file:
                    for chunk in crypto_object.decrypt(text, str(CONFIG_PASSWORD), key_length=32):
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

                crypto_object = self.getCryptoObject()
                text = payload[8:]
                with open(swap_path, 'wb') as out_file:
                    for chunk in crypto_object.decrypt(text, str(CONFIG_PASSWORD), key_length=32):
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