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
    # insert test data
    Session = sessionmaker(bind=engine)
    session = Session()

    test_dir = Catalog('relrin_main')
    session.add(test_dir)
    session.commit()

    test_fs = FileSpace('relrin_fs', test_dir)
    session.add(test_fs)
    session.commit()

    free_acct = AccountType('free', 0.00)
    business_acct = AccountType('business', 100.00)
    corporate_acct = AccountType('corporate', 500.00)
    session.add_all([free_acct, business_acct, corporate_acct])
    session.commit()

    permissions = [Permission('Full control under system'),
                   Permission('Full control under users'),
                   Permission('Create directories'),
                   Permission('Rename'),
                   Permission('Delete'),
                   Permission('Write'),
                   Permission('Read')]
    session.add_all(permissions)
    session.commit()

    groups = [Group('anonymous'),
              Group('user'),
              Group('admin'),
              Group('root')]
    session.add_all(groups)
    session.commit()

    groups[0].permissions += [permissions[6]]
    groups[1].permissions += [permissions[2], permissions[3],
                              permissions[4], permissions[5],
                              permissions[6]]
    groups[2].permissions += [permissions[1], permissions[2],
                              permissions[3], permissions[4],
                              permissions[5], permissions[6]]
    groups[3].permissions += permissions
    session.commit()

    hash_pswd = str(sha256('123456'+'1').hexdigest())
    test_user = Users('relrin', 'Valery Savich', hash_pswd, 'some@mail.com',
                      '2015-01-01', 1, 3, 1)
    session.add(test_user)
    session.commit()

    session.close()
    print "Insertion data has complete!"

    print "\nTest query: Getting data from [Users] table..."
    result = engine.execute(text("select name, fullname, password from users"))
    for row in result:
        print "Users<name=%s, fullname=%s, password=%s>" % (row.name,
                                                            row.fullname,
                                                            row.password)


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-c", "--crtdb", dest='cdb',
                      help="Create database", default=False)
    parser.add_option("-i", "--initdb", dest="idb",
                      help="Initialize DB: insert test data", default=False)
    (options, args) = parser.parse_args()

    options.cdb = bool(options.cdb)
    options.idb = bool(options.idb)
    if options.cdb:
        create_db()
    if options.idb:
        initialize_db()
