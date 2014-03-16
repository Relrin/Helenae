from optparse import OptionParser
from hashlib import sha256

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

    test_dir = Catalog('relrin_main')
    session.add(test_dir)
    session.commit()

    #test_file = File('test.txt', '123456.txt', hash('123456.txt'), 1024, 0, 1)
    #test_file.server_id.append(test_server)
    #session.add(test_file)
    #session.commit()

    test_fs = FileSpace('relrin_fs', test_dir)
    session.add(test_fs)
    session.commit()

    free_acct = AccountType('free', 0.00)
    business_acct = AccountType('business', 100.00)
    corporate_acct = AccountType('corporate', 500.00)
    session.add_all([free_acct, business_acct, corporate_acct])
    session.commit()

    # bits in permissions:
    # [0] - full control under system
    # [1] - full control under users
    # [2] - create directories
    # [3] - rename
    # [4] - delete
    # [5] - write
    # [6] - read
    anonymous_gr = Group('anonymous', 1000000)
    users_gr = Group('users', 1111100)
    admins_gr = Group('admins', 1111110)
    root_gr = Group('root', 1111111)
    session.add_all([anonymous_gr, users_gr, admins_gr, root_gr])
    session.commit()

    hash_pswd = str(sha256('123456'+'1').hexdigest())
    test_user = Users('relrin', 'Valery Savich', hash_pswd, 'some@mail.com', '01.01.2015', 1, 2, 1)
    session.add(test_user)
    session.commit()

    session.close()
    print "Insertion data has complete!"

    print "\nTest query: Getting data from [Users] table..."
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
