import sys
from json import dumps, loads

import sqlalchemy
from sqlalchemy.orm import sessionmaker
from twisted.internet import reactor, ssl
from twisted.python import log, logfile
from twisted.web.server import Site
from twisted.web.static import File
from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol, listenWS

import commands
from db.tables import Users


# TODO: Add logger (from Twisted, not original library)
# TODO: Create PLUGIN architecture (using twistd)
# TODO: Define PostgreSQL DB structure
# TODO: Authentication under PostgreSQL+SQLAlchemy ORM
# TODO: Errors/Exceptions processing
# TODO: If hacking account or DDoS server or using unsupported commands - ban IP for 1-3 minutes (save IP at DB)

log_file = logfile.LogFile("service.log", ".")
log.startLogging(log_file)
engine = sqlalchemy.create_engine('postgresql://Relrin:05909333@localhost/csan', pool_size=20, max_overflow=0)


class DFSServerProtocol(WebSocketServerProtocol):

    commands = commands.commands_user

    def __init__(self):
        # initialize sessionmaker, which get access to work with DB
        # DONT FORGET use after all "self.sesison.close()"!!!
        self.Session = sessionmaker(bind=engine)
        self.commands_handlers = self.__initHandlersUser()

    def __initHandlersUser(self):
        """
            Initialize handlers for every command
        """
        handlers = commands.commands_handlers_server
        handlers['AUTH'] = self.authorization
        handlers['READ'] = None
        handlers['WRTE'] = None
        handlers['DELT'] = None
        handlers['RNME'] = None
        handlers['SYNC'] = None
        handlers['LIST'] = None
        return handlers

    def authorization(self, data):
        """
            Checking user with DB
        """
        log.msg("[AUTH] User=%s trying to auth..." % data['user'])
        session = self.Session()
        result = session.execute(sqlalchemy.select([Users]).where(Users.name == data['user']))
        result = result.fetchone()
        session.close()
        data, result_msg = commands.AUTH(result, data)
        log.msg(result_msg)
        return data

    def onMessage(self, payload, isBinary):
        """
            Processing request from user and send response
        """
        json_data = loads(payload)
        json_auth = json_data['auth']
        json_cmd  = json_data['cmd']
        # add there checking in DB for banned user or not...
        # for none-authorized users
        if json_auth == False:
            # first action with server --> authorization
            if json_cmd == 'AUTH':
                json_data = self.commands_handlers['AUTH'](json_data)
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
    else:
        debug = False

    contextFactory = ssl.DefaultOpenSSLContextFactory('keys/server.key', 'keys/server.crt')

    factory = WebSocketServerFactory("wss://localhost:9000", debug = debug, debugCodePaths = debug)
    factory.protocol = DFSServerProtocol
    factory.setProtocolOptions(allowHixie76 = True)

    listenWS(factory, contextFactory)

    webdir = File("./web/")
    webdir.contentTypes['.crt'] = 'application/x-x509-ca-cert'
    web = Site(webdir)

    reactor.listenSSL(8080, web, contextFactory)
    #reactor.listenTCP(8080, web)

    reactor.run()
