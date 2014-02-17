import sqlalchemy as sql


# Creating DB
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'
    id = sql.Column(sql.Integer, primary_key=True)
    name = sql.Column(sql.String, unique=True)
    fullname = sql.Column(sql.String)
    password = sql.Column(sql.String)

    def __init__(self, name, fullname, password):
        self.name = name
        self.fullname = fullname
        self.password = hash(password)

    def __repr__(self):
        return "<User('%s','%s', '%s')>" % (self.name, self.fullname, self.password)


if __name__ == '__main__':
    from sqlalchemy import text
    from sqlalchemy.orm import sessionmaker
    engine = sql.create_engine('postgresql://Relrin:05909333@localhost/csan')

    # defined tables at this file are created in selected DB
    Base.metadata.create_all(engine)

    # insert test data
    Session = sessionmaker(bind=engine)
    session = Session()
    test = Users('relrin', 'Valery Savich', hash('123456'))
    session.add(test)
    session.commit()
    session.close()

    # test query
    connection = engine.connect()
    result = engine.execute(text("select name, fullname, password from users"))
    for row in result:
        print "name%s --> fullname=%s --> password=%s" % (row.name, row.fullname, row.password)