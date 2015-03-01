Helenae	[![Build Status](https://travis-ci.org/Relrin/Helenae.svg)](https://travis-ci.org/Relrin/Helenae)
=======

Simplest analog of distributed file storages such as DropBox/SugarSync/etc.

Using
-------
- Python 2.7.5
- PostgreSQL
- Twisted
- Autobahn.ws
- OpenSSL
- SQLAlchemy ORM
- Flask
- pytest
- wxPython
- PyCrypto

Implemented features
-------
- opening/writing/transfering file or catalog
- rename/remove file or catalog
- synchronization files
- encryption by AES-256
- console/GUI clients
- supporting multiple file servers

Screenshots:
-------
Client GUI:
    ![alt text](https://raw.githubusercontent.com/Relrin/Helenae/master/screenshots/client_gui.png)

Running
-------

For start working with distributed file storage you will need:  
1) Run the server.py by doing

    python server.py [port]

2) Start few (minimum one) file servers

    # take example of fs.json
    python fileserver.py [path_to_config.json] [port]

3) Open in your browser

    https://localhost:8080/
    
or run the Python console client

    python client_console.py [port]
    
or run the Python GUI client

    python client_gui.py

Creating Server Keys and Certificates
-------------------------------------

TLS server keys and certificate can be generated by doing:

	openssl genrsa -out server.key 2048
	openssl req -new -key server.key -out server.csr
	openssl x509 -req -days 3650 -in server.csr -signkey server.key -out server.crt
	openssl x509 -in server.crt -out server.pem

To run the server 2 files are required.

Private key (with *no* passphrase set!):

	server.key

Certificate:

	server.crt

Thanks
-------------------------------------

Big thanks to:
- Jean-Paul Calderone [creator of Twisted] for help and advices on event-based programming with Twisted
- Tobias Oberstein [creator of Autobahn.ws] for programming tips on Autobahn.ws

Especially thanks http://www.fatcow.com/ for free icons
