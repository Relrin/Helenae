from time import gmtime, strftime

import sqlamp
from sqlalchemy import create_engine, MetaData
from sqlalchemy import Integer, DateTime, Float, Boolean, String, Column, ForeignKey, Table
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

    # Flask-Login integration
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    # Required for administrative interface
    def __unicode__(self):
        return unicode(self.name)


class AccountType(Base):
    __tablename__ = 'acctype'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(String, nullable=False)
    cost = Column(Float, nullable=False)

    def __init__(self, name="unknown", cost=0, description=''):
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

    def __init__(self, name="unknown", permission=0):
        self.name = name
        self.permission = permission

    def __repr__(self):
        return "<Group('%s','%s')>" % (self.name, self.permission)


class FileSpace(Base):
    __tablename__ = 'filespace'
    id = Column(Integer, primary_key=True)
    storage_name = Column(String, nullable=False, unique=True)
    created_time = Column(DateTime, nullable=False)
    catalog_id = relationship("Catalog")

    def __init__(self, name="un", catalog=None):
        self.storage_name = name
        self.created_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        if catalog is not None:
            self.catalog_id.append(catalog)

    def __repr__(self):
        return "<FileSpace('%s','%s','%s')>" % (self.id, self.storage_name, self.created_time)


class Catalog(Base):
    __tablename__ = 'catalog'
    __mp_manager__ = 'mp'
    id = Column(Integer, primary_key=True)
    directory_name = Column(String, nullable=False, unique=True)
    last_modified = Column(DateTime, nullable=False)
    public_folder = Column(Boolean, nullable=False)
    file_id = relationship("File")
    parent_id = Column(ForeignKey('catalog.id'), index=True)
    parent = relation("Catalog", remote_side=[id])
    fs_id = Column(Integer, ForeignKey('filespace.id'))

    def __init__(self, dir_name, public_folder=False, parent=None):
        self.directory_name = dir_name
        self.last_modified = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        self.public_folder = public_folder
        self.parent = parent

    def __repr__(self):
        return "<Catalog('%s','%s','%s')>" % (self.directory_name, self.last_modified, self.public_folder)


association_table = Table('m2m_file_server', Base.metadata,
                          Column('id', Integer, primary_key=True),
                          Column('file_id', Integer, ForeignKey('file.id')),
                          Column('fileserver_id', Integer, ForeignKey('fileserver.id'))
                          )


class File(Base):
    __tablename__ = 'file'
    id = Column(Integer, primary_key=True)
    original_name = Column(String, nullable=False)
    server_name = Column(String, nullable=False)
    file_hash = Column(String, nullable=False)
    chunk_size = Column(Integer, nullable=False)
    chunk_number = Column(Integer, nullable=False)
    catalog_id = Column(Integer, ForeignKey("catalog.id"))
    server_id = relationship("FileServer", secondary=association_table)

    def __init__(self, orig_name, serv_name, file_hash, chunk_size, chunk_number, catalog_id):
        self.original_name = orig_name
        self.server_name = serv_name
        self.file_hash = file_hash
        self.chunk_size = chunk_size
        self.chunk_number = chunk_number
        self.catalog_id = catalog_id

    def __repr__(self):
        return "<File('%s','%s','%s','%d')>" % (self.original_name, self.server_name, self.file_hash, self.chunk_size)


class FileServer(Base):
    __tablename__ = 'fileserver'
    id = Column(Integer, primary_key=True)
    ip = Column(String, nullable=False)
    port = Column(Integer, nullable=False)
    status = Column(String)
    last_online = Column(DateTime)

    def __init__(self, ip='127.0.0.1', port='9999', status="OFFLINE"):
        self.ip = ip
        self.port = port
        self.status = status
        self.last_online = strftime("%Y-%m-%d %H:%M:%S", gmtime())

    def __repr__(self):
        return "<FileServer('%s','%d','%s','%s')>" % (self.ip, self.port, self.status, self.last_online)
