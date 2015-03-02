import os
import sys
import pickle
from json import dumps, loads
from hashlib import sha256
from subprocess import Popen, PIPE, STDOUT

from twisted.internet import reactor, ssl
from twisted.internet.task import deferLater
from twisted.python import log, logfile
from twisted.web.server import Site
from twisted.web.wsgi import WSGIResource
from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol, listenWS

from balancer.balancer import Balancer
from db.queries import Queries
from flask_app import app
from utils import commands


# TODO: Create PLUGIN architecture (using twistd)
# TODO: Errors/Exceptions processing

POLL_TIME = 300    # polling file servers every 5 min
log_file = logfile.LogFile("service.log", ".")
log.startLogging(log_file)


def checkServerStatus(ip, port):
    """
        File server status checker
        After communication return result as string "IP|PORT|STATUS"
    """
    p = Popen(["python", "./utils/statuschecker.py", str(ip), str(port)], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    result = p.communicate()[0].replace('\n', '')
    return result.split('|')


class DFSServerProtocol(WebSocketServerProtocol):

    commands = commands.commands_server

    def __init__(self):
        self.lstFS = []
        self.commands_handlers = self.__initHandlersUser()
        self.balancer = Balancer()
        d = deferLater(reactor, 5, self.__pollServers)

    def __updateStatusDB(self):
        """
            Updating status field in DB for every available server
        """
        dump = self.lstFS
        Queries.updateServersStatus(dump)

    def __pollServers(self):
        """
            Polling all available file servers
        """
        def getResult(result):
            self.lstFS.append(result)

        log.msg("[POLL] Start daemon for polling servers...")
        servers = Queries.getAllFileServers()
        for server in servers:
            dlGetStatus = deferLater(reactor, 0, checkServerStatus, server.ip, server.port).addCallback(getResult)
        dlUpdateDB = deferLater(reactor, 0, self.__updateStatusDB)
        dlUpdate = deferLater(reactor, 5, self.__updateFileServerList)

    def __updateFileServerList(self):
        """
            Periodical update data about servers in balancer
        """
        self.balancer.updateFileServerList(self.lstFS)
        self.lstFS = []
        log.msg("[POLL] Polling process has complete!")
        d = deferLater(reactor, POLL_TIME, self.__pollServers)

    def __initHandlersUser(self):
        """
            Initialize handlers for every command
        """
        handlers = commands.commands_handlers_server
        handlers['REGS'] = self.registration
        handlers['FSRV'] = self.fileserver_auth
        handlers['AUTH'] = self.authorization
        handlers['READ'] = self.read_fs
        handlers['WRTE'] = self.write_file
        handlers['DELT'] = self.delete_file
        handlers['RNME'] = self.rename_file
        handlers['SYNC'] = self.fileSync
        handlers['CRLN'] = self.create_link
        handlers['LINK'] = self.download_by_link
        handlers['LIST'] = self.get_fs_structure
        # for gui app
        handlers['REAF'] = self.read_fs_all
        handlers['GETF'] = self.get_all_user_files
        handlers['WRTF'] = self.massive_write_files
        handlers['DELF'] = self.massive_delete_files
        handlers['RENF'] = self.massive_rename_files
        return handlers

    def registration(self, data):
        log.msg("[REGS] New user=%s: want to create account" % (data['user']))
        try:
            checker = Queries.getSimilarUsers(data['user'])
            if len(checker) == 0:
                if len(data['user']) < 3:
                    raise ValueError('Length of username was been more than 3 symbols!')
                elif len(data['password']) < 6:
                    raise ValueError('Length of password was been more than 6 symbols!')
                elif len(data['fullname']) == 0:
                    raise ValueError("Full name can't be empty!")

                log.msg("[REGS] Creating new user...")
                catalog_name = str(data['user'] + "_main")
                fs_name = str(data['user'] + "_fs")
                Queries.createNewUser(catalog_name, fs_name, data['user'], data['password'], data['fullname'], data['email'])
                data['error'] = []
                data['auth'] = True
                data['cmd'] = 'CREG'
                log.msg("[REGS] All operations successfully completed!")
            else:
                log.msg("[REGS] User with ID=%s already contains at DB" % (data['user']))
                data['error'].append('ERROR: This user already exists! Please, check another login...')
                data['cmd'] = 'RREG'
        except ValueError, exc:
            data['error'].append('ERROR: %s' % exc.message)
            data['cmd'] = 'RREG'
        return data

    def fileserver_auth(self, data):
        connection_data, port = data
        result = {}
        log.msg("[FSRV] Adding new fileserver into DB with IP=%s, PORT=%d" % (connection_data.host, port))
        checker = Queries.getFileServerByIpAndPort(connection_data.host, port)
        if len(checker) == 0:
            log.msg("[FSRV] Successfully added!")
            Queries.createNewFileServer(connection_data.host, port)
            result['errors'] = ''
        else:
            log.msg("[FSRV] Files server with IP=%s, PORT=%d already contains at DB" % (connection_data.host, port))
            result['errors'] = 'Already exists!'
        return result

    def authorization(self, data):
        """
            Checking user with DB
        """
        log.msg("[AUTH] User=%s trying to auth..." % data['user'])
        result = Queries.getUser(data['user'])
        result_msg = "[AUTH] User=%s successfully logged..." % data['user']
        # user not found at DB
        if result is None:
            data['cmd'] = 'RAUT'
            data['error'].append('\nWARNING: User not found')
            result_msg = "[AUTH] User=%s not found" % data['user']
        else:
            if result['name'] == data['user']:
                # correct users info --> real user
                hash_psw = str(sha256(data['password']+str(result['id'])).hexdigest())
                if result['password'] == str(hash_psw):
                    data['auth'] = True
                # incorrect password --> fake user
                else:
                    data['cmd'] = 'RAUT'
                    data['error'].append('\nERROR: Incorrect password. Try again...')
                    result_msg = "[AUTH] Incorrect password for user=%s" % data['user']
        log.msg(result_msg)
        return data

    def write_file(self, data):
        """
            Checking user with DB
        """
        log.msg("[WRTE] User=%s trying to write file..." % data['user'])
        server = self.balancer.getFileServer(data['cmd'], data['file_hash'])
        if server is None:
            msg = "ERROR: Can't write now your file: servers in offline. Try later..."
            data['cmd'] = 'AUTH'
            data['error'].append(msg)
            log.msg(log.msg("[WRTE] %s..." % msg))
        else:
            # get info from DB
            user_db = Queries.getUser(data['user'])
            fs = Queries.getFileSpace(user_db.filespace_id)
            catalog = Queries.getUserCatalogOnFilespace(fs.id)
            server_ip = str(server[0])
            port = int(server[1])
            cnt_files = Queries.getCountFiles() + 1
            # processing data
            user_path, original_filename = os.path.split(data['file_path'])
            if not data['gui']:
                user_path = u''
            filename, type_file = os.path.splitext(original_filename)
            user_id = 'u' + str(user_db.id).rjust(14, '0')
            file_id = str(cnt_files).rjust(25-len(type_file), '0') + type_file
            data['server'] = server
            data['json'] = ('WRITE_FILE', user_id, file_id, data['file_path'])
            # write record into DB
            Queries.createFileRecordOneChunk(original_filename, file_id, data['file_hash'], user_path,
                                             data['file_size'], catalog.id, server_ip, port)
            log.msg(log.msg("[WRTE] Operation with DB and User=%s has complete..." % data['user']))
            data['cmd'] = 'COWF'
        del data['file_path']
        del data['file_hash']
        del data['file_size']
        return data

    def __get_files(self, user_id):
        """
            Get files from DB
        """
        result = None, None, None
        files, servers, userID = Queries.getAllFileRecords(user_id)
        if len(files) > 0:
            result = files, servers, userID
        return result

    def get_fs_structure(self, data):
        """
            Get list of all written file by some user
        """
        log.msg('[LIST] Getting data for User=%s' % (data['user']))
        files, servers, user_ids = self.__get_files(str(data['user']))
        data['files'] = pickle.dumps(files)
        data['servers'] = pickle.dumps(servers)
        data['user_ids'] = user_ids
        data['cmd'] = 'CLST'
        log.msg('[LIST] Getting data for User=%s has complete!' % (data['user']))
        return data

    def read_fs(self, data):
        """
            Building serialized file list
        """
        server = Queries.getFileServer(data['file_hash'])
        if server is None:
            msg = "ERROR: Can't read now your file: servers in offline. Try later..."
            data['cmd'] = 'AUTH'
            data['error'].append(msg)
            log.msg(log.msg("[READ] %s..." % msg))
        else:
            log.msg('[READ] Getting data for User=%s' % (data['user']))
            data['cmd'] = 'CREA'
            log.msg('[READ] Getting data for User=%s has complete!' % (data['user']))
        return data

    def read_fs_all(self, data):
        """
            Getting all data, which need for read all files (filename, path, server id and port)
        """
        log.msg('[REAF] Getting data for User=%s' % (data['user']))
        files_lst = []
        fs_name = str(data['user'] + "_fs")
        user_db = Queries.getUser(data['user'])
        user_id = 'u' + str(user_db.id).rjust(14, '0')
        fs_db = Queries.getFileSpaceByName(fs_name)
        catalog = Queries.getUserCatalogOnFilespace(fs_db.id)
        for name, path in data['files_read']:
            user_file, user_file_servers = Queries.getFirstFileRecord(name, path, catalog.id)
            files_lst.append((name, path, user_file.server_name, user_file_servers))
        data['cmd'] = 'CREA'
        data['user_id'] = user_id
        data['files_read'] = files_lst
        log.msg('[REAF] Getting data for User=%s has complete!' % (data['user']))
        return data

    def delete_file(self, data):
        """
            Delete file from record, and after this - from server
        """
        server = Queries.getFileServer(data['file_hash'])
        if server is None:
            msg = "ERROR: Can't delete now your file: servers in offline. Try later..."
            data['cmd'] = 'AUTH'
            data['error'].append(msg)
            log.msg(log.msg("[DELT] %s..." % msg))
        else:
            log.msg('[DELT] Delete data for User=%s' % (data['user']))
            Queries.deleteFileRecordByID(data['file_path'])
            data['cmd'] = 'CDLT'
            log.msg('[DELT] Delete data for User=%s has complete!' % (data['user']))
        del data['file_path']
        return data

    def rename_file(self, data):
        """
            Renaming file on DB (NOT on file servers!)
        """
        log.msg('[RNME] Rename file by User=%s' % (data['user']))
        dict_file = {"original_name": data['new_name']}
        file_id = data['file_id']
        Queries.updateFileRecordData(file_id, dict_file)
        data['cmd'] = 'CRNM'
        log.msg('[RNME] Rename file by User=%s has complete!' % (data['user']))
        del data['file_id']
        del data['new_name']
        return data

    def fileSync(self, data):
        """
            Synchronization files using rsync tool
        """
        server = []
        user_db = Queries.getUser(data['user'])
        user_id = 'u' + str(user_db.id).rjust(14, '0')
        # when want to sync more than one file...
        for file in data['files_u']:
            original_name = file[0]
            server_name = file[1]
            file_hash = file[2]
            file_hash_new = file[3][0]
            file_size = file[3][1]
            fs = Queries.getFileServer(file_hash)
            if file_hash != file_hash_new and data['sync_type'] == 'WSYNC_FILE':
                dict_file = {"file_hash": file_hash_new, "chunk_size": file_size}
                Queries.updateFileRecordDataByHash(original_name, file_hash, dict_file)
            server.append((original_name, server_name) + (fs if fs else (None,)))
        data['server'] = server
        data['user_id'] = user_id
        data['cmd'] = 'CSYN'
        log.msg('[SYNC] SYNC data for User=%s has complete!' % (data['user']))
        del data['files_u']
        return data

    def get_all_user_files(self, data):
        log.msg('[GETF] Getting all files for User=%s' % (data['user']))
        files_lst = []
        fs_name = str(data['user'] + "_fs")
        files = Queries.getAllFileRecordsIter(fs_name)
        for record in files.yield_per(1):
            files_lst.append((record.original_name, record.user_path))
        data['cmd'] = 'READ'
        data['files_read'] = files_lst
        log.msg('[GETF] GETF data for User=%s has complete!' % (data['user']))
        return data

    def massive_write_files(self, data):
        """
            Massive write files to file storage.
            If file already exists, then synchronize with him.
        """
        log.msg('[WRTF] Massive write files for User=%s' % (data['user']))
        files_lst = []
        fs_name = str(data['user'] + "_fs")
        user_db = Queries.getUser(data['user'])
        user_id = 'u' + str(user_db.id).rjust(14, '0')
        fs_db = Queries.getFileSpaceByName(fs_name)
        catalog = Queries.getUserCatalogOnFilespace(fs_db.id)
        for name, path, file_hash_new, size in data['files_write']:
            file_path = path.replace(data['default_dir'] , '')
            user_file, user_file_servers = Queries.getFirstFileRecord(name, file_path, catalog.id)
            # if file not exists, then add record to database and write file in fileserver
            if user_file is None:
                server = self.balancer.getFileServer("WRTE", file_hash_new)
                if server is not None:
                    server_ip = str(server[0])
                    port = int(server[1])
                    cnt_files = Queries.getCountFiles() + 1
                    # processing data
                    filename, type_file = os.path.splitext(name)
                    file_id = str(cnt_files).rjust(25-len(type_file), '0') + type_file
                    # write record into DB
                    Queries.createFileRecordOneChunk(name, file_id, file_hash_new, file_path, size, catalog.id, server_ip, port)
                    servers = []
                    servers.append((server_ip, port))
                    files_lst.append(('WRITE_FILE', name, path, file_id, servers))
            # if file already exists, then just sync with file on fileserver
            elif user_file.file_hash != file_hash_new:
                Queries.updateFirstFileRecordHashAndSize(user_file.id, file_hash_new, size)
                files_lst.append(('WSYNC_FILE', name, path, user_file.server_name, user_file_servers))
        data['cmd'] = 'CWRT'
        data['user_id'] = user_id
        data['files_write'] = files_lst
        log.msg('[WRTF] WRTF for User=%s has complete!' % (data['user']))
        return data

    def massive_delete_files(self, data):
        """
            Massive delete files from file storage
        """
        log.msg('[DELF] Delete data for User=%s' % (data['user']))
        user_db = Queries.getUser(data['user'])
        user_id = 'u' + str(user_db.id).rjust(14, '0')
        del_files = Queries.deleteManyFileRecords(data['deleted_files'], data['default_dir'])
        data['cmd'] = 'CDLT'
        data['user_id'] = user_id
        data['deleted_files'] = del_files
        log.msg('[DELF] Delete data for User=%s has complete!' % (data['user']))
        return data

    def massive_rename_files(self, data):
        """
            Rename one file on massive filepaths in folder
        """
        log.msg('[RENF] Rename files for User=%s' % (data['user']))
        for name, path, file_hash, new_filename, new_file_path in data['rename_files']:
            Queries.updateFirstFileRecordNameAndPath(name, path, file_hash, new_filename, new_file_path)
        data['cmd'] = 'CREN'
        log.msg('[RENF] Rename files for User=%s has complete!' % (data['user']))
        del data['rename_files']
        return data

    def create_link(self, data):
        log.msg("[CRLN] Create link on file for User=%s" % (data['user']))
        if len(data['file_info']) == 4:
            try:
                filename, file_hash, relative_path, key = data['file_info']
                description = data.get('description', '')
                url = Queries.createLinkOnFile(data['user'], filename, file_hash,
                                               relative_path, key, description)
                data['url'] = url
            except Exception, exc:
                data['url'] = None
                data['error'].append(exc.message)
        data['cmd'] = 'CCLN'
        log.msg('[CRLN] Create link on file for User=%s has complete!' % (data['user']))
        del data['file_info']
        del data['description']
        return data

    def download_by_link(self, data):
        """
            Return to user connection info only by some link
        """
        log.msg("[LINK] Return file servers on file for User=%s" % (data['user']))
        servers = []
        user_id = server_filename = filename = key = None
        link = data.get('url', None)
        if link:
            user_db, server_filename, filename, key, servers = Queries.getFileServerByUserLink(link)
            if user_db:
                user_id = 'u' + str(user_db).rjust(14, '0')
        data['user_id'] = user_id
        data['file_info'] = (server_filename, filename, key, servers)
        data['cmd'] = 'CLNK'
        log.msg("[LINK] Return file servers on file for User=%s" % (data['user']))
        del data['url']
        return data

    def onMessage(self, payload, isBinary):
        """
            Processing request from user and send response
        """
        json_data = loads(payload)
        json_auth = json_data['auth']
        json_cmd = json_data['cmd']
        # if this fileserver
        if json_cmd == 'FSRV' and json_data['user'] == 'FS' and json_auth is True:
            ip = self.transport.getPeer()
            response = dumps(self.fileserver_auth((ip, json_data['server_port'])))
        # or some user
        else:
            # add there checking in DB for banned user or not...
            # for none-authorized users
            if json_auth is False:
                # first action with server --> authorization
                if json_cmd == 'AUTH':
                    json_data = self.commands_handlers['AUTH'](json_data)
                if json_cmd == 'REGS':
                    json_data = self.commands_handlers['REGS'](json_data)
            # for authorized users
            else:
                if json_cmd in commands.commands_server.keys():
                    if self.commands_handlers[json_cmd] is not None:
                        json_data = self.commands_handlers[json_cmd](json_data)
                    # just send error if not realized
                    else:
                        json_data['error'].append('ERROR: %s command is not already realized...' % json_cmd)
                # its not real commands on server --> send error
                # this guy trying to hacking/DDoS server? also reset auth and set ban for 1-3 minutes
                else:
                    json_data['auth'] = False
                    json_data['error'].append('ERROR: This command is not supported on server...')
            response = dumps(json_data)
        self.sendMessage(str(response), sync=True)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'debug':
        log.startLogging(sys.stdout)
        debug = True
        port = int(sys.argv[2])
    else:
        debug = False
        port = int(sys.argv[1])

    contextFactory = ssl.DefaultOpenSSLContextFactory('web/keys/server.key', 'web/keys/server.crt')

    server_addr = "wss://localhost:%d" % (port)
    factory = WebSocketServerFactory(server_addr, debug = debug, debugCodePaths = debug)
    factory.protocol = DFSServerProtocol
    factory.setProtocolOptions(allowHixie76 = True)

    listenWS(factory, contextFactory)

    # Flask with SSL under Twisted
    resource = WSGIResource(reactor, reactor.getThreadPool(), app)
    site = Site(resource)
    reactor.listenSSL(8080, site, contextFactory)
    # reactor.listenTCP(8080, web)
    reactor.run()
