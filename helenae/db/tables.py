from time import gmtime, strftime

import sqlamp
from sqlalchemy import create_engine, MetaData
from sqlalchemy import Integer, DateTime, Float, BigInteger, Boolean, String, Column, ForeignKey, Table
from sqlalchemy.orm import relationship, relation
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('postgresql://user:password@localhost/csan')
metadata = MetaData(engine)
Base = declarative_base(metadata=metadata, metaclass=sqlamp.DeclarativeMeta)


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(25), unique=True)
    fullname = Column(String)
    password = Column(String)
    email = Column(String)
    subscription_time_left = Column(DateTime)
    acctype_id = Column(Integer, ForeignKey('acctype.id'), index=True)
    group_id = Column(Integer, ForeignKey('group.id'), index=True)
    filespace_id = Column(Integer, ForeignKey('filespace.id'), index=True)

    def __init__(self, name, fullname, password, email, sub_time_left, acctype, group, fs):
        self.name = name
        self.fullname = fullname
        self.password = password
        self.email = email
        self.subscription_time_left = sub_time_left
        self.acctype_id = acctype
        self.group_id = group
        self.filespace_id = fs

    def __repr__(self):
        return "<User('%s','%s','%s','%s','%s','%d','%d')>" % (self.name, self.fullname, self.password, self.email,
                                                               self.subscription_time_left, self.acctype_id,
                                                               self.group_id)


class AccountType(Base):
    __tablename__ = 'acctype'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(String, nullable=False)
    cost = Column(Float, nullable=False)

    def __init__(self, name, cost, description=''):
        self.name = name
        self.cost = cost
        self.description = description

    def __repr__(self):
        return "<AccountType('%s','%.3f','%s')>" % (self.name, self.cost, self.description)


class Group(Base):
    __tablename__ = 'group'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    permission = Column(Integer, nullable=False)

    def __init__(self, name, permission):
        self.name = name
        self.permission = permission

    def __repr__(self):
        return "<Group('%s','%s')>" % (self.name, self.permission)


class FileSpace(Base):
    __tablename__ = 'filespace'
    id = Column(Integer, primary_key=True)
    storage_name = Column(String, nullable=False, unique=True)
    created_time = Column(DateTime, nullable=False)

    def __init__(self, name):
        self.storage_name = name
        self.created_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())

    def __repr__(self):
        return "<FileSpace('%s','%s')>" % (self.name, self.created_time)


class Catalog(Base):
    __tablename__ = 'catalog'
    __mp_manager__ = 'mp'
    id = Column(Integer, primary_key=True)
    directory_name = Column(String, nullable=False)
    last_modified = Column(DateTime, nullable=False)
    public_folder = Column(Boolean, nullable=False)
    file_id = relationship("File")
    parent_id = Column(ForeignKey('catalog.id'), index=True)
    parent = relation("Catalog", remote_side=[id])

    def __init__(self, dir_name, public_folder=False, parent=None):
        self.directory_name = dir_name
        self.last_modified = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        self.public_folder = public_folder
        self.parent = parent

    def __repr__(self):
        return "<Catalog('%s','%s','%s')>" % (self.directory_name, self.last_modified, self.public_folder)


class m2m_file_server(Base):
    __tablename__ = 'm2m_file_server'
    id = Column(Integer, primary_key=True)
    chunk_number = Column(Integer, nullable=False)
    chunk_size = Column(Integer, nullable=False)
    file_id = Column(Integer, ForeignKey('file.id'), index=True)
    server_id = Column(Integer, ForeignKey('fileserver.id'), index=True)
    child = relationship("FileServer")

    def __repr__(self):
        return "<m2m_File_Server('%d','%d','%d','%d','%s')>" % (self.chunk_number, self.chunk_size, self.file_id,
                                                                self.server_id, self.child)


class File(Base):
    __tablename__ = 'file'
    id = Column(Integer, primary_key=True)
    original_name = Column(String, nullable=False)
    server_name = Column(String, nullable=False)
    file_hash = Column(String, nullable=False)
    filesize = Column(BigInteger)
    catalog_id = Column(Integer, ForeignKey("catalog.id"))
    server_id = relationship("m2m_file_server")

    def __init__(self, orig_name, serv_name, file_hash, filesize, catalog_id):
        self.original_name = orig_name
        self.server_name = serv_name
        self.file_hash = file_hash
        self.filesize = filesize
        self.catalog_id = catalog_id

    def __repr__(self):
        return "<File('%s','%s','%s','%d')>" % (self.original_name, self.server_name, self.file_hash, self.filesize)


class FileServer(Base):
    __tablename__ = 'fileserver'
    id = Column(Integer, primary_key=True)
    ip = Column(String, nullable=False)
    port = Column(Integer, nullable=False)
    status = Column(String)
    last_online = Column(DateTime)

    def __init__(self, ip, port, status):
        self.ip = ip
        self.port = port
        self.status = status
        self.last_online = strftime("%Y-%m-%d %H:%M:%S", gmtime())

    def __repr__(self):
        return "<FileServer('%s','%d','%s','%s')>" % (self.ip, self.port, self.status, self.last_online)


if __name__ == '__main__':
    from sqlalchemy import text
    from sqlalchemy.orm import sessionmaker

    # defined tables at this file are created in selected DB
    Base.metadata.create_all(engine)

    # insert test data
    Session = sessionmaker(bind=engine)
    session = Session()

    # test_server = FileServer('192.168.1.1', 80, 'online')
    # session.add(test_server)
    # session.commit()

    # test_dir = Catalog('test')
    # session.add(test_dir)
    # session.commit()
    
    # test_dir = Catalog('test')
    # session.add(test_dir)
    # session.commit()
    
    # test_file = File('test.txt', '123456.txt', hash('123456.txt'), 1024, 1)
    # session.add(test_file)
    # test_dir.file_id.append(test_file)
    # session.commit()
    # test_m2m = m2m_file_server(chunk_size=0, chunk_number=0)
    # test_m2m.child = test_server
    # test_file.server_id.append(test_m2m)
    # session.commit()

    test_fs = FileSpace('test')
    session.add(test_fs)
    session.commit()
    
    test_acctype = AccountType('free', 0.00)
    session.add(test_acctype)
    session.commit()
    
    test_group = Group('users', 1101)
    session.add(test_group)
    session.commit()

    test_user = Users('relrin', 'Valery Savich', hash('123456'), 'some@mail.com', '01.01.2014', 1, 1, 1)
    session.add(test_user)
    session.commit()

    session.close()

    # test query
    connection = engine.connect()
    result = engine.execute(text("select name, fullname, password from users"))
    for row in result:
        print "name=%s --> fullname=%s --> password=%s" % (row.name, row.fullname, row.password)
