from optparse import OptionParser

import sqlalchemy.exc
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

from tables import *


def create_db():
    """
        Defined tables at tables.py file are created in some DB
    """
    try:
        Base.metadata.create_all(engine)
    except sqlalchemy.exc.InvalidRequestError:
        print "SQLAlchemy ERROR: SQLAlchemy was asked to do something it can't do"
    except sqlalchemy.exc.DBAPIError, exc:
        print "SQLAlchemy ERROR: %s", (exc)
    except sqlalchemy.exc.SQLAlchemyError, exc:
        print "SQLAlchemy ERROR: %s", (exc)

def initialize_db():
    """
        This code inserting testing data into defined tables
    """
    #insert test data
    Session = sessionmaker(bind=engine)
    session = Session()

    test_dir = Catalog('test')
    session.add(test_dir)
    session.commit()

    #test_file = File('test.txt', '123456.txt', hash('123456.txt'), 1024, 0, 1)
    #test_file.server_id.append(test_server)
    #session.add(test_file)
    #session.commit()

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
    print "Insertion data has complete!"

    print "Test query: Getting data from [Users] table\n"
    connection = engine.connect()
    result = engine.execute(text("select name, fullname, password from users"))
    for row in result:
        print "Users<name=%s, fullname=%s, password=%s>" % (row.name, row.fullname, row.password)



if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-c", "--crtdb", dest='cdb', help = "Create database", default=False)
    parser.add_option("-i", "--initdb", dest = "idb", help = "Initialize DB: insert test data", default=False)
    (options, args) = parser.parse_args()

    options.cdb = bool(options.cdb)
    options.idb = bool(options.idb)
    if options.cdb:
        create_db()
    if options.idb:
        initialize_db()
