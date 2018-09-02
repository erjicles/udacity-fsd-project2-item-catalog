from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item
import json
from flask import make_response
import requests

app = Flask(__name__)

APPLICATION_NAME = "Item Catalog Application"

# Connect to Database and create database session
engine = create_engine('sqlite:///itemcatalog.db',
    connect_args={'check_same_thread': False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Landing page - show all categories and recent items
@app.route('/')
@app.route('/category/')
def showCategories():
    categories = session.query(Category).order_by(asc(Category.name)).all()
    latestItems = session.query(Item).order_by(desc(Item.id)).limit(10).all()
    return render_template('categories.html', 
        categories=categories,
        latestItems=latestItems)


# Create a new category
@app.route('/category/new/', methods=['GET', 'POST'])
def newCategory():
    if request.method == 'POST':
        newCategory = Category(
            name=request.form['name'])
        session.add(newCategory)
        session.commit()
        return redirect(url_for('showCategories'))
    else:
        return render_template('newcategory.html')


# Edit an existing category
@app.route('/category/<int:category_id>/edit/', methods=['GET', 'POST'])
def editCategory(category_id):
    editedCategory = session.query(
        Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedCategory.name = request.form['name']
            session.add(editedCategory)
            session.commit()
            return redirect(url_for('showCategories'))
    else:
        return render_template('editcategory.html', category=editedCategory)


# Delete a category
@app.route('/category/<int:category_id>/delete/', methods=['GET', 'POST'])
def deleteCategory(category_id):
    categoryToDelete = session.query(
        Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        session.delete(categoryToDelete)
        session.commit()
        return redirect(url_for('showCategories'))
    else:
        return render_template('deleteCategory.html', category=categoryToDelete)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)