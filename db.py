from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


engine = create_engine('mysql://root:mahdirb3479@localhost:3306/crypto')
Session = sessionmaker(bind=engine)
session = Session()