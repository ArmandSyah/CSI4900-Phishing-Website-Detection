from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///web_assets.sqlite') #Create test.sqlite automatically
Base = declarative_base()

class Web_Assets(Base): 
    __tablename__ = 'web_assets'

    id = Column(Integer, primary_key=True)
    netloc = Column(String)
    filename = Column(String)
    hexdigest = Column(String)
    extension = Column(String)

    def __init__(self, netloc, filename, hexdigest, extension):
        self.netloc = netloc
        self.filename = filename
        self.hexdigest = hexdigest
        self.extension = extension

def create_database():
    Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

if __name__ == "__main__":
    create_database()