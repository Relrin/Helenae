import os
import sys
import datetime
import pickle
from json import dumps, loads
from hashlib import sha256
from time import gmtime, strftime
from subprocess import Popen, PIPE, STDOUT

import sqlalchemy
import sqlalchemy.exc
from sqlalchemy import and_, func, asc
from sqlalchemy.orm import sessionmaker
from twisted.internet import reactor, ssl
from twisted.internet.task import deferLater
from twisted.python import log, logfile
from twisted.web.server import Site
from twisted.web.wsgi import WSGIResource
from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol, listenWS

from balancer.balancer import Balancer
from db.tables import File as FileTable
from db.tables import Users, FileServer, FileSpace, Catalog
from flask_app import app
from utils import commands


# TODO: Create PLUGIN architecture (using twistd)
# TODO: Errors/Exceptions processing

POLL_TIME = 300    # polling file servers every 5 min
log_file = logfile.LogFile("service.log", ".")
log.startLogging(log_file)
engine = sqlalchemy.create_engine('postgresql://user:password@localhost/csan', pool_size=20, max_overflow=0)


def checkServerStatus(ip, port):
    """
        File server status checker
        After communication return result as string "IP|PORT|STATUS"
    """
    p = Popen(["python", "./utils/statuschecker.py", str(ip), str(port)], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    result = p.communicate()[0].replace('\n', '')
    return result.split('|')


class DFSServerProtocol(WebSocketServerProtocol):

    commands = commands.commands_user

    def __init__(self):
        # initialize sessionmaker, which get access to work with DB
        # DONT FORGET use after all "self.sesison.close()"!!!
        self.lstFS = []
        self.Session = sessionmaker(bind=engine)
        self.commands_handlers = self.__initHandlersUser()
        self.balancer = Balancer()
        d = deferLater(reactor, 5, self.__pollServers)

    def __create_session(self):
        session = self.Session()
        session._model_changes = {}
        return session

    def __updateStatusDB(self):
        """
            Updating status field in DB for every available server
        """
        dump = self.lstFS
        session = self.__create_session()
        for server in dump:
            ip = server[0]
            port = server[1]
            status = server[2]
            dict_status = {"status": unicode(status)}
            if status == 'ONLINE':
                dict_status["last_online"] = strftime("%Y-%m-%d %H:%M:%S", gmtime())
            session.query(FileServer).filter_by(ip=ip, port=port).update(dict_status)
            session.commit()
        session.close()

    def __pollServers(self):
        """
            Polling all available file servers
        """
        def getResult(result):
            self.lstFS.append(result)

        log.msg("[POLL] Start daemon for polling servers...")
        poll_session = self.__create_session()
        servers = poll_session.execute(sqlalchemy.select([FileServer]))
        servers = servers.fetchall()
        poll_session.close()
        for server in servers:
            dlGetStatus = deferLater(reactor, 0, checkServerStatus, server.ip, server.port).addCallback(getResult)
        dlUpdateDB = deferLater(reactor, 0, self.__updateStatusDB)
        dlUpdate = deferLater(reactor, 5, self.__updateFileServerList)

    def __getFileServerDB(self, file_hash):
        try:
            session = self.__create_session()
            result = session.query(FileTable).filter_by(file_hash=file_hash).first()
            if result is not None:
                if result.server_id[0].status != 'OFFLINE':
                    result = (result.server_id[0].ip, result.server_id[0].port)
        except sqlalchemy.exc.ArgumentError:
            log.msg('SQLAlchemy ERROR: Invalid or conflicting function argument is supplied')
        except sqlalchemy.exc.CompileError:
            log.msg('SQLAlchemy ERROR: Error occurs during SQL compilation')
        finally:
            session.close()
        return result


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
        handlers['LIST'] = self.get_fs_structure
        return handlers

    def registration(self, data):
        log.msg("[REGS] New user=%s: want to create account" % (data['user']))
        try:
            session = self.__create_session()
            checker = session.execute(sqlalchemy.select([Users])
                                                .where(Users.name == data['user'])
                                     )
            checker = checker.fetchall()
            if len(checker) == 0:
                if len(data['user']) < 3:
                    raise ValueError('Length of username was been more than 3 symbols!')
                elif len(data['password']) < 6:
                    raise ValueError('Length of password was been more than 6 symbols!')
                elif len(data['fullname']) == 0:
                    raise ValueError("Full name can't be empty!")

                log.msg("[REGS] Creating special main catalog for new user...")
                #catalog_name = str(data['user'] + "_main_" + strftime("%d%m%Y", gmtime()))
                catalog_name = str(data['user'] + "_main")
                new_dir = Catalog(catalog_name)
                session.add(new_dir)
                session.commit()

                log.msg("[REGS] Creating file space for new user...")
                #fs_name = str(data['user'] + "fs_" + strftime("%d%m%Y", gmtime()))
                fs_name = str(data['user'] + "_fs")
                new_fs = FileSpace(fs_name, new_dir)
                session.add(new_fs)
                session.commit()

                log.msg("[REGS] Add new user into DB...")
                fs = session.execute(sqlalchemy.select([FileSpace])
                                               .where(FileSpace.storage_name == fs_name)
                                     )
                fs = fs.fetchone()
                time_is = datetime.datetime.strptime(strftime("%d.%m.%Y", gmtime()), "%d.%m.%Y").date()
                time_is = time_is + datetime.timedelta(days=365)
                date_max = time_is.strftime("%d.%m.%Y")
                id_new = session.execute(func.count(Users.id)).fetchone()[0] + 1
                password_hash = str(sha256(data['password']+str(id_new)).hexdigest())
                new_user = Users(data['user'], data['fullname'], password_hash, data['email'], date_max, 1, 2, fs.id)
                session.add(new_user)
                session.commit()
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
        except sqlalchemy.exc.ArgumentError, e:
            log.msg('SQLAlchemy ERROR: Invalid or conflicting function argument is supplied')
        except sqlalchemy.exc.CompileError:
            log.msg('SQLAlchemy ERROR: Error occurs during SQL compilation')
        finally:
            session.close()
        return data

    def fileserver_auth(self, data):
        connection_data, port = data
        result = {}
        log.msg("[FSRV] Adding new fileserver into DB with IP=%s, PORT=%d" % (connection_data.host, port))
        try:
            session = self.__create_session()
            checker = session.execute(sqlalchemy.select([FileServer])
                                                .where(and_(FileServer.ip == connection_data.host, FileServer.port == port))
                                     )
            checker = checker.fetchall()
            if len(checker) == 0:
                log.msg("[FSRV] Successfully added!")
                new_fs = FileServer(connection_data.host, port, 'ONLINE')
                session.add(new_fs)
                session.commit()
                result['errors'] = ''
            else:
                log.msg("[FSRV] Files server with IP=%s, PORT=%d already contains at DB" % (connection_data.host, port))
                result['errors'] = 'Already exists!'
        except sqlalchemy.exc.ArgumentError:
            log.msg('SQLAlchemy ERROR: Invalid or conflicting function argument is supplied')
        except sqlalchemy.exc.CompileError:
            log.msg('SQLAlchemy ERROR: Error occurs during SQL compilation')
        finally:
            session.close()
        return result

    def authorization(self, data):
        """
            Checking user with DB
        """
        log.msg("[AUTH] User=%s trying to auth..." % data['user'])
        try:
            session = self.__create_session()
            result = session.execute(sqlalchemy.select([Users]).where(Users.name == data['user']))
            result = result.fetchone()
            data, result_msg = commands.AUTH(result, data)
            log.msg(result_msg)
        except sqlalchemy.exc.ArgumentError:
            log.msg('SQLAlchemy ERROR: Invalid or conflicting function argument is supplied')
        except sqlalchemy.exc.CompileError:
            log.msg('SQLAlchemy ERROR: Error occurs during SQL compilation')
        finally:
            session.close()
        return data

    def write_file(self, data):
        """
            Checking user with DB
        """
        log.msg("[WRTE] User=%s trying to write file..." % data['user'])
        try:
            session = self.__create_session()
            server = self.balancer.getFileServer(data['cmd'], data['file_hash'])
            if server is None:
                msg = "ERROR: Can't write now your file: servers in offline. Try later..."
                data['cmd'] = 'AUTH'
                data['error'].append(msg)
                log.msg(log.msg("[WRTE] %s..." % msg))
            else:
                # get info from DB
                user_db = session.execute(sqlalchemy.select([Users])
                                                    .where(Users.name == data['user'])
                                          ).fetchone()
                fs = session.execute(sqlalchemy.select([FileSpace])
                                               .where(FileSpace.id == user_db.filespace_id)
                                     ).fetchone()
                catalog = session.execute(sqlalchemy.select([Catalog])
                                                    .where(Catalog.fs_id == fs.id)
                                                    .order_by(asc(Catalog.id))
                                          ).fetchone()
                server_ip = str(server[0])
                port = int(server[1])
                fileserver = session.query(FileServer).filter_by(ip=server_ip, port=port).first()
                cnt_files = session.execute(func.count(FileTable.id)).fetchone()[0] + 1
                # processing data
                user_path, original_filename = os.path.split(data['file_path'])
                if not data['gui']:
                    user_path = u''
                filename, type_file = original_filename.split('.')
                user_id = 'u' + str(user_db.id).rjust(14, '0')
                file_id = str(cnt_files).rjust(24-len(type_file), '0') + '.' + type_file
                data['server'] = server
                data['json'] = ('WRITE_FILE', user_id, file_id, data['file_path'])
                # write record into DB
                new_file = FileTable(original_filename, file_id, data['file_hash'], user_path, data['file_size'], 0, catalog.id)
                new_file.server_id.append(fileserver)
                session.add(new_file)
                session.commit()
                log.msg(log.msg("[WRTE] Operation with DB and User=%s has complete..." % data['user']))
                data['cmd'] = 'COWF'
        except sqlalchemy.exc.ArgumentError:
            log.msg('SQLAlchemy ERROR: Invalid or conflicting function argument is supplied')
        except sqlalchemy.exc.CompileError:
            log.msg('SQLAlchemy ERROR: Error occurs during SQL compilation')
        finally:
            del data['file_path']
            del data['file_hash']
            del data['file_size']
            session.close()
        return data

    def __get_files(self, user_id):
        """
            Get files from DB
        """
        result = None, None, None
        try:
            session = self.__create_session()
            user = session.execute(sqlalchemy.select([Users])
                                             .where(Users.name == user_id)
                                   ).fetchone()
            catalog = session.execute(sqlalchemy.select([Catalog])
                                                .where(Catalog.fs_id == user.filespace_id)
                                      ).fetchone()
            files = session.query(FileTable).filter_by(catalog_id=catalog.id).all()
            if len(files) > 0:
                result = files, [file.server_id for file in files], user.id
        except sqlalchemy.exc.ArgumentError:
            log.msg('SQLAlchemy ERROR: Invalid or conflicting function argument is supplied')
        except sqlalchemy.exc.CompileError:
            log.msg('SQLAlchemy ERROR: Error occurs during SQL compilation')
        finally:
            session.close()
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
        server = self.__getFileServerDB(data['file_hash'])
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

    def delete_file(self, data):
        """
            Delete file from record, and after this - from server
        """
        server = self.__getFileServerDB(data['file_hash'])
        try:
            session = self.__create_session()
            if server is None:
                msg = "ERROR: Can't delete now your file: servers in offline. Try later..."
                data['cmd'] = 'AUTH'
                data['error'].append(msg)
                log.msg(log.msg("[DELT] %s..." % msg))
            else:
                log.msg('[DELT] Delete data for User=%s' % (data['user']))
                file = session.query(FileTable).filter_by(id=data['file_path']).first()
                servers = file.server_id[:]
                for server in servers:
                    file.server_id.remove(server)
                session.commit()
                session.delete(file)
                session.commit()
                data['cmd'] = 'CDLT'
                log.msg('[DELT] Delete data for User=%s has complete!' % (data['user']))
        except sqlalchemy.exc.ArgumentError:
            log.msg('SQLAlchemy ERROR: Invalid or conflicting function argument is supplied')
        except sqlalchemy.exc.CompileError:
            log.msg('SQLAlchemy ERROR: Error occurs during SQL compilation')
        finally:
            session.close()
        del data['file_path']
        return data

    def rename_file(self, data):
        """
            Renaming file on DB (NOT on file servers!)
        """
        try:
            session = self.__create_session()
            log.msg('[RNME] Rename file by User=%s' % (data['user']))
            dict_file = {"original_name": data['new_name']}
            file_id = data['file_id']
            session.query(FileTable).filter_by(id=file_id).update(dict_file)
            session.commit()
            data['cmd'] = 'CRNM'
            log.msg('[RNME] Rename file by User=%s has complete!' % (data['user']))
        except sqlalchemy.exc.ArgumentError:
            log.msg('SQLAlchemy ERROR: Invalid or conflicting function argument is supplied')
        except sqlalchemy.exc.CompileError:
            log.msg('SQLAlchemy ERROR: Error occurs during SQL compilation')
        finally:
            session.close()
        del data['file_id']
        del data['new_name']
        return data

    def fileSync(self, data):
        """
            Synchronization files using rsync tool
        """
        try:
            server = None
            session = self.__create_session()
            user_db = session.execute(sqlalchemy.select([Users])
                                                .where(Users.name == data['user'])
                                     ).fetchone()
            user_id = 'u' + str(user_db.id).rjust(14, '0')
            # when want to sync more than one file...
            server = []
            for file in data['files_u']:
                original_name = file[0]
                server_name = file[1]
                file_hash = file[2]
                fs = self.__getFileServerDB(file_hash)
                server.append((original_name, server_name) + (fs if fs else (None,)))
            data['server'] = server
            data['user_id'] = user_id
            data['cmd'] = 'CSYN'
            log.msg('[SYNC] SYNC data for User=%s has complete!' % (data['user']))
        except sqlalchemy.exc.ArgumentError:
            log.msg('SQLAlchemy ERROR: Invalid or conflicting function argument is supplied')
        except sqlalchemy.exc.CompileError:
            log.msg('SQLAlchemy ERROR: Error occurs during SQL compilation')
        finally:
            session.close()
            del data['files_u']
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
                if json_cmd in commands.commands_user.keys():
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
