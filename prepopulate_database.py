from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item

# Connect to Database and create database session
engine = create_engine('sqlite:///itemcatalog.db',
    connect_args={'check_same_thread': False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Add initial categories
categories = []
categories.append(Category(name="Soccer"))
categories.append(Category(name="Basketball"))
categories.append(Category(name="Baseball"))
categories.append(Category(name="Frisbee"))
categories.append(Category(name="Snowboarding"))
categories.append(Category(name="Rock Climbing"))
categories.append(Category(name="Foosball"))
categories.append(Category(name="Skating"))
categories.append(Category(name="Hockey"))
for category in categories:
    session.add(category)
session.commit()