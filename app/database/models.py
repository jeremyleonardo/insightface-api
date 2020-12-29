from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Text, UniqueConstraint, MetaData, Table
from app.database.custom_types import Cube

# _metadata = MetaData()

# faces = Table('faces', _metadata, 
#     Column('id', Integer, primary_key=True),
#     Column('name', String),
#     Column('age', Integer),
#     Column('gender', String(1),
#     Column('embedding', Cube('float8[]')),
#     Column('created_at', DateTime),
#     Column('updated_at', DateTime)
#     )

Base = declarative_base()

class Face(Base):
    __tablename__ = 'faces'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)
    gender = Column(String(1))
    embedding = Column(Cube)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    __table_args__ = (
        UniqueConstraint('name'),
        )

    def __repr__(self):
        return "<Face(name='%s', age='%d', gender='%s')>" % (
            self.name, self.age, self.gender)