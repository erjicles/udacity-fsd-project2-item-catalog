from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item

# Connect to Database and create database session
engine = create_engine('postgresql+psycopg2:///itemcatalog')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Add initial categories
if session.query(Category).count() == 0:
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


# Add initial items
if session.query(Item).count() == 0:
    items = []
    items.append(Item(name="Soccer ball", category_id=1))
    items.append(Item(name="Hoop", category_id=2))
    items.append(Item(name="Bat", category_id=3))
    items.append(Item(name="Disc", category_id=4))
    items.append(Item(name="Board", category_id=5))
    items.append(Item(name="Ropes", category_id=6))
    items.append(Item(name="Table", category_id=7))
    items.append(Item(name="Skates", category_id=8))
    items.append(Item(name="Stick", category_id=9))
    for item in items:
        session.add(item)
    session.commit()
