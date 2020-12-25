from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Text

Base = declarative_base()


class Face(Base):
    __tablename__ = 'face'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)
    gender = Column(String(1))
    embedding = Column(Text)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    def __repr__(self):
        return "<Face(name='%s', age='%d', gender='%s')>" % (
            self.name, self.age, self.gender)
        
