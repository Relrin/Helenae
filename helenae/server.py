import sys

from json import dumps, loads

import sqlalchemy
from sqlalchemy.orm import sessionmaker
from db.create_db import Users

from twisted.internet import reactor, ssl
from twisted.python import log
from twisted.web.server import Site
from twisted.web.static import File

from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol, listenWS

# TODO: Add logger (from Twisted, not original library)
# TODO: Create PLUGIN architecture (using twistd)
# TODO: Define PostgreSQL DB structure
# TODO: Authentication under PostgreSQL+SQLAlchemy ORM
# TODO: Errors/Exceptions processing

engine = sqlalchemy.create_engine('postgresql://Relrin:05909333@localhost/csan', pool_size=20, max_overflow=0)


class DFSServerProtocol(WebSocketServerProtocol):

    def __init__(self):
        # get object from connection pool and create session
        # DONT FORGET use after all "self.sesison.close()"!!!
        self.Session = sessionmaker(bind=engine)

    def __del__(self):
        self.session.close()

    def authorization(self, data):
        """
            Checking user with DB
        """
        session = self.Session()
        result = session.execute(sqlalchemy.select([Users]).where(Users.name == data['user']))
        result = result.fetchone()
        if result is None:
            data['cmd'] = 'RAUT'
            data['error'] = 'User not found'
        else:
            if result['name'] == data['user']:
                # correct users info --> real user
                if result['password'] == data['password']:
                    data['cmd'] = 'HELP'
                    data['auth'] = True
                # incorrect password --> fake user
                else:
                    data['cmd'] = 'RAUT'
                    data['error'] = 'Incorrect password. Try again...'
        session.close()
        return data

    def onMessage(self, payload, isBinary):
        """
            Processing request from user and send response
        """
        json_data = loads(payload)
        # for none-authorized users
        if json_data['auth'] == False:
            # first action with server --> authorization
            if json_data['cmd'] == 'AUTH':
                json_data = self.authorization(json_data)
        # for authorized users
        else:
            pass
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

    webdir = File(".")
    webdir.contentTypes['.crt'] = 'application/x-x509-ca-cert'
    web = Site(webdir)

    reactor.listenSSL(8080, web, contextFactory)
    #reactor.listenTCP(8080, web)

    reactor.run()
