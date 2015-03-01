import datetime
import os
from hashlib import sha256, sha1
from time import gmtime, strftime

import sqlalchemy
import sqlalchemy.exc
from sqlalchemy import and_, func, asc
from sqlalchemy.orm import sessionmaker

from tables import File as FileTable
from tables import Users, FileServer, FileSpace, Catalog, Link

engine = sqlalchemy.create_engine('postgresql://user:password@localhost/csan', pool_size=20, max_overflow=0)
Session = sessionmaker(bind=engine)


class Queries():

    @staticmethod
    def createSession():
        session = Session()
        session._model_changes = {}
        return session

    #-------------------------------------------------------------------------

    @staticmethod
    def getCountFiles():
        """
            Returns count of records in Files table
        """
        result = 0
        session = Queries.createSession()
        try:
            result = session.execute(func.count(FileTable.id)).fetchone()[0]
        except sqlalchemy.exc.ArgumentError:
            print 'SQLAlchemy ERROR: Invalid or conflicting function argument is supplied'
        except sqlalchemy.exc.CompileError:
            print 'SQLAlchemy ERROR: Error occurs during SQL compilation'
        finally:
            session.close()
        return result

    #-------------------------------------------------------------------------

    @staticmethod
    def getUser(username):
        """
            Get user record from DB based on his unique login
        """
        result = None
        session = Queries.createSession()
        try:
            result = session.execute(sqlalchemy.select([Users]).where(Users.name == username))
            result = result.fetchone()
        except sqlalchemy.exc.ArgumentError:
            print 'SQLAlchemy ERROR: Invalid or conflicting function argument is supplied'
        except sqlalchemy.exc.CompileError:
            print 'SQLAlchemy ERROR: Error occurs during SQL compilation'
        finally:
            session.close()
        return result

    @staticmethod
    def getSimilarUsers(username):
        """
            Get all user, which similar on %username% from DB
        """
        result = None
        session = Queries.createSession()
        try:
            checker = session.execute(sqlalchemy.select([Users])
                                      .where(Users.name == username)
            )
            result = checker.fetchall()
        except sqlalchemy.exc.ArgumentError:
            print 'SQLAlchemy ERROR: Invalid or conflicting function argument is supplied'
        except sqlalchemy.exc.CompileError:
            print 'SQLAlchemy ERROR: Error occurs during SQL compilation'
        finally:
            session.close()
        return result

    @staticmethod
    def getUserCatalogOnFilespace(fs_id):
        """
            Get users catalog from DB based on filespace id
        """
        result = None
        session = Queries.createSession()
        try:
            result = session.execute(sqlalchemy.select([Catalog])
                                     .where(Catalog.fs_id == fs_id)
                                     .order_by(asc(Catalog.id))
            ).fetchone()
        except sqlalchemy.exc.ArgumentError:
            print 'SQLAlchemy ERROR: Invalid or conflicting function argument is supplied'
        except sqlalchemy.exc.CompileError:
            print 'SQLAlchemy ERROR: Error occurs during SQL compilation'
        finally:
            session.close()
        return result

    @staticmethod
    def getFileSpace(fs_id):
        """
            Get filespace record based on his ID
        """
        result = None
        session = Queries.createSession()
        try:
            result = session.execute(sqlalchemy.select([FileSpace])
                                     .where(FileSpace.id == fs_id)
            ).fetchone()
        except sqlalchemy.exc.ArgumentError:
            print 'SQLAlchemy ERROR: Invalid or conflicting function argument is supplied'
        except sqlalchemy.exc.CompileError:
            print 'SQLAlchemy ERROR: Error occurs during SQL compilation'
        finally:
            session.close()
        return result

    @staticmethod
    def getFileSpaceByName(fs_name):
        """
            Get filespace record based on his storage name
        """
        result = None
        session = Queries.createSession()
        try:
            result = session.execute(sqlalchemy.select([FileSpace]).where(FileSpace.storage_name == fs_name)).fetchone()
        except sqlalchemy.exc.ArgumentError:
            print 'SQLAlchemy ERROR: Invalid or conflicting function argument is supplied'
        except sqlalchemy.exc.CompileError:
            print 'SQLAlchemy ERROR: Error occurs during SQL compilation'
        finally:
            session.close()
        return result

    @staticmethod
    def getFileServer(file_hash):
        """
            Getting some file server from DB based on hash
        """
        result = None
        session = Queries.createSession()
        try:
            result = session.query(FileTable).filter_by(file_hash=file_hash).first()
            if result is not None:
                if result.server_id[0].status != 'OFFLINE':
                    result = (result.server_id[0].ip, result.server_id[0].port)
        except sqlalchemy.exc.ArgumentError:
            print 'SQLAlchemy ERROR: Invalid or conflicting function argument is supplied'
        except sqlalchemy.exc.CompileError:
            print 'SQLAlchemy ERROR: Error occurs during SQL compilation'
        finally:
            session.close()
        return result

    @staticmethod
    def getFileServerByIpAndPort(ip, port):
        """
            Get file server from DB, based on his ip and port
        """
        result = None
        session = Queries.createSession()
        try:
            checker = session.execute(sqlalchemy.select([FileServer])
                                      .where(and_(FileServer.ip == ip, FileServer.port == port))
            )
            result = checker.fetchall()
        except sqlalchemy.exc.ArgumentError:
            print 'SQLAlchemy ERROR: Invalid or conflicting function argument is supplied'
        except sqlalchemy.exc.CompileError:
            print 'SQLAlchemy ERROR: Error occurs during SQL compilation'
        finally:
            session.close()
        return result

    @staticmethod
    def getAllFileServers():
        """
            Getting list of all file servers
        """
        servers = None
        session = Queries.createSession()
        try:
            servers = session.execute(sqlalchemy.select([FileServer]))
            servers = servers.fetchall()
        except sqlalchemy.exc.ArgumentError:
            print 'SQLAlchemy ERROR: Invalid or conflicting function argument is supplied'
        except sqlalchemy.exc.CompileError:
            print 'SQLAlchemy ERROR: Error occurs during SQL compilation'
        finally:
            session.close()
        return servers

    @staticmethod
    def getAllFileRecords(user_id):
        """
            Get all File records from DB
        """
        files_db = userID = servers = None
        session = Queries.createSession()
        try:
            user = session.execute(sqlalchemy.select([Users])
                                   .where(Users.name == user_id)
            ).fetchone()
            userID = user.id
            catalog = session.execute(sqlalchemy.select([Catalog])
                                      .where(Catalog.fs_id == user.filespace_id)
            ).fetchone()
            files_db = session.query(FileTable).filter_by(catalog_id=catalog.id).all()
            servers = [file.server_id for file in files_db]
        except sqlalchemy.exc.ArgumentError:
            print 'SQLAlchemy ERROR: Invalid or conflicting function argument is supplied'
        except sqlalchemy.exc.CompileError:
            print 'SQLAlchemy ERROR: Error occurs during SQL compilation'
        finally:
            session.close()
        return files_db, servers, userID

    @staticmethod
    def getAllFileRecordsIter(fs_name):
        """
            Get all File records from DB with iterations
        """
        files = None
        session = Queries.createSession()
        try:
            fs_db = session.execute(sqlalchemy.select([FileSpace]).where(FileSpace.storage_name == fs_name)).fetchone()
            catalog = session.execute(sqlalchemy.select([Catalog]).where(Catalog.fs_id == fs_db.id)).fetchone()
            files = session.query(FileTable).filter_by(catalog_id=catalog.id)
        except sqlalchemy.exc.ArgumentError:
            print 'SQLAlchemy ERROR: Invalid or conflicting function argument is supplied'
        except sqlalchemy.exc.CompileError:
            print 'SQLAlchemy ERROR: Error occurs during SQL compilation'
        finally:
            session.close()
        return files


    @staticmethod
    def getFirstFileRecord(name, path, catalog_id):
        """
            Get first record from list, based on original_name of file, his path and catalog ID
        """
        file_db = file_servers = None
        session = Queries.createSession()
        try:
            file_db = session.query(FileTable).filter_by(catalog_id=catalog_id, original_name=name, user_path=path).first()
            if file_db is not None:
                file_servers = [(server.ip, server.port) for server in file_db.server_id]
        except sqlalchemy.exc.ArgumentError:
            print 'SQLAlchemy ERROR: Invalid or conflicting function argument is supplied'
        except sqlalchemy.exc.CompileError:
            print 'SQLAlchemy ERROR: Error occurs during SQL compilation'
        finally:
            session.close()
        return file_db, file_servers

    #-------------------------------------------------------------------------

    @staticmethod
    def createNewUser(catalog_name, filestorage_name, username, password, fullname, email):
        """
            Create new user in DB
        """
        session = Queries.createSession()
        try:
            # create new Catalog
            new_dir = Catalog(catalog_name)
            session.add(new_dir)
            session.commit()
            # create new FileStorage
            new_fs = FileSpace(filestorage_name, new_dir)
            session.add(new_fs)
            session.commit()
            # create new User
            fs = session.execute(sqlalchemy.select([FileSpace])
                                 .where(FileSpace.storage_name == filestorage_name)
            )
            fs = fs.fetchone()
            time_is = datetime.datetime.strptime(strftime("%d.%m.%Y", gmtime()), "%d.%m.%Y").date()
            time_is = time_is + datetime.timedelta(days=365)
            date_max = time_is.strftime("%d.%m.%Y")
            id_new = session.execute(func.count(Users.id)).fetchone()[0] + 1
            password_hash = str(sha256(password+str(id_new)).hexdigest())
            new_user = Users(username, fullname, password_hash, email, date_max, 1, 2, fs.id)
            session.add(new_user)
            session.commit()
        except sqlalchemy.exc.ArgumentError:
            print 'SQLAlchemy ERROR: Invalid or conflicting function argument is supplied'
        except sqlalchemy.exc.CompileError:
            print 'SQLAlchemy ERROR: Error occurs during SQL compilation'
        finally:
            session.close()


    @staticmethod
    def createNewFileServer(ip, port):
        """
            Append new file server record
        """
        session = Queries.createSession()
        try:
            new_fs = FileServer(ip, port, 'ONLINE')
            session.add(new_fs)
            session.commit()
        except sqlalchemy.exc.ArgumentError:
            print 'SQLAlchemy ERROR: Invalid or conflicting function argument is supplied'
        except sqlalchemy.exc.CompileError:
            print 'SQLAlchemy ERROR: Error occurs during SQL compilation'
        finally:
            session.close()

    @staticmethod
    def createFileRecordOneChunk(original_filename, file_id, file_hash, user_path, file_size, catalog_id, server_ip, server_port):
        """
            Create record in DB for one file (one file - one chunk, which equal size of file)
        """
        session = Queries.createSession()
        try:
            fileserver = session.query(FileServer).filter_by(ip=server_ip, port=server_port).first()
            new_file = FileTable(original_filename, file_id, file_hash, user_path, file_size, 0, catalog_id)
            new_file.server_id.append(fileserver)
            session.add(new_file)
            session.commit()
        except sqlalchemy.exc.ArgumentError:
            print 'SQLAlchemy ERROR: Invalid or conflicting function argument is supplied'
        except sqlalchemy.exc.CompileError:
            print 'SQLAlchemy ERROR: Error occurs during SQL compilation'
        finally:
            session.close()

    @staticmethod
    def createLinkOnFile(user, filename, file_hash, relative_path, key, description=''):
        session = Queries.createSession()
        try:
            file_record = session.query(FileTable).filter_by(
                original_name=filename,
                file_hash=file_hash,
                user_path=relative_path
            ).first()
            normalized_path = os.path.normpath(relative_path)
            hash_link = sha1('{0}/{1}/{2}'.format(filename,
                                                  file_hash,
                                                  datetime.datetime.now())
            ).hexdigest()
            url = 'http://127.0.0.1:8080/{0}/{1}/{2}'.format(user, normalized_path, hash_link)
            expire_date = datetime.datetime.now() + datetime.timedelta(days=7)
            new_link = Link(url=url, expire_date=expire_date, key=key, description=description, file_id=file_record.id)
            session.add(new_link)
            session.commit()
        except sqlalchemy.exc.ArgumentError:
            print 'SQLAlchemy ERROR: Invalid or conflicting function argument is supplied'
        except sqlalchemy.exc.CompileError:
            print 'SQLAlchemy ERROR: Error occurs during SQL compilation'
        finally:
            session.close()
        return url

    #-------------------------------------------------------------------------

    @staticmethod
    def updateServersStatus(servers):
        """
            Updating status field in DB for every available server
        """
        session = Queries.createSession()
        try:
            for server in servers:
                ip = server[0]
                port = server[1]
                status = server[2]
                dict_status = {"status": unicode(status)}
                if status == 'ONLINE':
                    dict_status["last_online"] = strftime("%Y-%m-%d %H:%M:%S", gmtime())
                session.query(FileServer).filter_by(ip=ip, port=port).update(dict_status)
                session.commit()
        except sqlalchemy.exc.ArgumentError:
            print 'SQLAlchemy ERROR: Invalid or conflicting function argument is supplied'
        except sqlalchemy.exc.CompileError:
            print 'SQLAlchemy ERROR: Error occurs during SQL compilation'
        finally:
            session.close()

    @staticmethod
    def updateFileRecordData(file_id, updated_data):
        """
            Update file record, based on his ID. Also using updated data as dictionary with new values
        """
        session = Queries.createSession()
        try:
            session.query(FileTable).filter_by(id=file_id).update(updated_data)
            session.commit()
        except sqlalchemy.exc.ArgumentError:
            print 'SQLAlchemy ERROR: Invalid or conflicting function argument is supplied'
        except sqlalchemy.exc.CompileError:
            print 'SQLAlchemy ERROR: Error occurs during SQL compilation'
        finally:
            session.close()

    @staticmethod
    def updateFileRecordDataByHash(filename, file_hash, updated_data):
        """
            Update file record, based on his file hash and name. Also using updated data as dictionary with new values
        """
        session = Queries.createSession()
        try:
            session.query(FileTable).filter_by(original_name=filename, file_hash=file_hash).update(updated_data)
            session.commit()
        except sqlalchemy.exc.ArgumentError:
            print 'SQLAlchemy ERROR: Invalid or conflicting function argument is supplied'
        except sqlalchemy.exc.CompileError:
            print 'SQLAlchemy ERROR: Error occurs during SQL compilation'
        finally:
            session.close()

    @staticmethod
    def updateFirstFileRecordNameAndPath(name, file_path, file_hash, new_filename, new_file_path):
        """
            Update first record from list, based on original_name of file, his hash and path
        """
        session = Queries.createSession()
        try:
            user_file = session.query(FileTable).filter_by(original_name=name, user_path=file_path, file_hash=file_hash).first()
            if user_file is not None:
                if name != new_filename:
                    user_file.original_name = new_filename
                if file_path != new_file_path:
                    user_file.user_path = new_file_path
                session.commit()
        except sqlalchemy.exc.ArgumentError:
            print 'SQLAlchemy ERROR: Invalid or conflicting function argument is supplied'
        except sqlalchemy.exc.CompileError:
            print 'SQLAlchemy ERROR: Error occurs during SQL compilation'
        finally:
            session.close()

    @staticmethod
    def updateFirstFileRecordHashAndSize(file_id, new_hash, new_size):
        """
            Update first record from list, based on original_name of file, his hash and path
        """
        session = Queries.createSession()
        try:
            user_file = session.query(FileTable).filter_by(id=file_id).first()
            if user_file is not None:
                user_file.file_hash = new_hash
                user_file.chunk_size = new_size
                session.commit()
        except sqlalchemy.exc.ArgumentError:
            print 'SQLAlchemy ERROR: Invalid or conflicting function argument is supplied'
        except sqlalchemy.exc.CompileError:
            print 'SQLAlchemy ERROR: Error occurs during SQL compilation'
        finally:
            session.close()

    #-------------------------------------------------------------------------

    @staticmethod
    def deleteFileRecordByID(file_id):
        """
            Delete file record from DB, based on his ID
        """
        session = Queries.createSession()
        try:
            file_db = session.query(FileTable).filter_by(id=file_id).first()
            servers = file_db.server_id[:]
            for server in servers:
                file_db.server_id.remove(server)
            session.commit()
            session.delete(file_db)
            session.commit()
        except sqlalchemy.exc.ArgumentError:
            print 'SQLAlchemy ERROR: Invalid or conflicting function argument is supplied'
        except sqlalchemy.exc.CompileError:
            print 'SQLAlchemy ERROR: Error occurs during SQL compilation'
        finally:
            session.close()

    @staticmethod
    def deleteManyFileRecords(deleted_files, default_dir):
        """
            Massive delete files from DB.
        """
        del_files = []
        session = Queries.createSession()
        try:
            for name, path, file_hash, size in deleted_files:
                file_servers = []
                file_path = path.replace(default_dir, '')
                user_file = session.query(FileTable).filter_by(original_name=name, user_path=file_path, file_hash=file_hash).first()
                if user_file is not None:
                    servers = user_file.server_id[:]
                    for server in servers:
                        user_file.server_id.remove(server)
                        file_servers.append((server.ip, server.port))
                    del_files.append(('DELET_FILE', name, path, user_file.server_name, file_servers))
                    session.delete(user_file)
            session.commit()
        except sqlalchemy.exc.ArgumentError:
            print 'SQLAlchemy ERROR: Invalid or conflicting function argument is supplied'
        except sqlalchemy.exc.CompileError:
            print 'SQLAlchemy ERROR: Error occurs during SQL compilation'
        finally:
            session.close()
        return del_files
