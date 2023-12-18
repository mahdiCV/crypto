from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


engine = create_engine('mysql://root)
Session = sessionmaker(bind=engine)
session = Session()
