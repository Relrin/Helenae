import sys
import datetime
from json import dumps, loads
from hashlib import sha256
from time import gmtime, strftime
from subprocess import Popen, PIPE, STDOUT

import sqlalchemy
import sqlalchemy.exc
from sqlalchemy import and_
from sqlalchemy.orm import sessionmaker
from twisted.internet import reactor, ssl
from twisted.internet.task import deferLater
from twisted.python import log, logfile
from twisted.web.server import Site
from twisted.web.static import File
from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol, listenWS

import commands
from db.tables import Users, FileServer, FileSpace, Catalog
from balancer import Balancer

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
    p = Popen(["python", "./fileserver/statuschecker.py", str(ip), str(port)], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    result = p.communicate()[0].replace('\n','')
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

    def __updateStatusDB(self):
        """
            Updating status field in DB for every available server
        """
        dump = self.lstFS
        session = self.Session()
        for server in dump:
            ip = server[0]
            port = server[1]
            status = server[2]
            session.query(FileServer).filter_by(ip=ip, port=port).update({"status": unicode(status)})
            session.commit()
        session.close()

    def __pollServers(self):
        """
            Polling all available file servers
        """
        def getResult(result):
            self.lstFS.append(result)

        poll_session = self.Session()
        servers = poll_session.execute(sqlalchemy.select([FileServer]))
        servers = servers.fetchall()
        poll_session.close()
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
        d = deferLater(reactor, POLL_TIME, self.__pollServers)

    def __initHandlersUser(self):
        """
            Initialize handlers for every command
        """
        handlers = commands.commands_handlers_server
        handlers['REGS'] = self.registration
        handlers['FSRV'] = self.fileserver_auth
        handlers['AUTH'] = self.authorization
        handlers['READ'] = None
        handlers['WRTE'] = None
        handlers['DELT'] = None
        handlers['RNME'] = None
        handlers['SYNC'] = None
        handlers['LIST'] = None
        return handlers

    def registration(self, data):
        log.msg("[REGS] New user=%s: want to create account" % (data['user']))
        try:
            session = self.Session()
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
                catalog_name = str(data['user'] + "_main_" + strftime("%d%m%Y", gmtime()))
                new_dir = Catalog(catalog_name)
                session.add(new_dir)
                session.commit()

                log.msg("[REGS] Creating file space for new user...")
                fs_name = str(data['user'] + "fs_" + strftime("%d%m%Y", gmtime()))
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
                new_user = Users(data['user'], data['fullname'], str(sha256(data['password']).hexdigest()), data['email'], date_max, 1, 2, fs.id)
                session.add(new_user)
                session.commit()
                data['error'] = ''
                data['auth'] = True
                data['cmd'] = 'CREG'
                log.msg("[REGS] All operations successfully completed!")
            else:
                log.msg("[REGS] User with ID=%s already contains at DB" % (data['user']))
                data['error'] = 'This user already exists! Please, check another login...'
                data['cmd'] = 'RREG'
        except ValueError, exc:
            data['error'] = exc.message
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
            session = self.Session()
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
            session = self.Session()
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

    def onMessage(self, payload, isBinary):
        """
            Processing request from user and send response
        """
        json_data = loads(payload)
        json_auth = json_data['auth']
        json_cmd  = json_data['cmd']
        # if this fileserver
        if json_cmd == 'FSRV' and json_data['user'] == 'FS' and json_auth is True:
            ip = self.transport.getPeer()
            response = dumps(self.fileserver_auth((ip, json_data['server_port'])))
        # or some user
        else:
            # add there checking in DB for banned user or not...
            # for none-authorized users
            if json_auth == False:
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
                        json_data['error'] = '%s command is not already realized...' % json_cmd
                # its not real commands on server --> send error
                # this guy trying to hacking/DDoS server? also reset auth and set ban for 1-3 minutes
                else:
                    json_data['auth'] = False
                    json_data['error'] = 'This command is not supported on server...'
            response = dumps(json_data)
        self.sendMessage(str(response))

    def readFileStructure(self):
        """
            Get all files/folders/etc. structure from DB
        """
        pass

    def getServerParams(self):
        """
            Getting (IP, PORT) of "File Server" to read/write operations
        """
        pass

    def fileSync(self):
        """
            Synchronization files using rsync tool
        """
        pass

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'debug':
        log.startLogging(sys.stdout)
        debug = True
        port = int(sys.argv[2])
    else:
        debug = False
        port = int(sys.argv[1])

    contextFactory = ssl.DefaultOpenSSLContextFactory('keys/server.key', 'keys/server.crt')

    server_addr = "wss://localhost:%d" % (port)
    factory = WebSocketServerFactory(server_addr, debug = debug, debugCodePaths = debug)
    factory.protocol = DFSServerProtocol
    factory.setProtocolOptions(allowHixie76 = True)

    listenWS(factory, contextFactory)

    webdir = File("./web/")
    webdir.contentTypes['.crt'] = 'application/x-x509-ca-cert'
    web = Site(webdir)

    reactor.listenSSL(8080, web, contextFactory)
    #reactor.listenTCP(8080, web)

    reactor.run()
