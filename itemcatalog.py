from flask import Flask, render_template, request, redirect, jsonify, url_for, \
    flash
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from database_setup import Base, User, Category, Item
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog Application"

# Connect to Database and create database session
engine = create_engine(
    'postgresql+psycopg2://catalog:catalog@localhost/itemcatalog')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Used to form a json response with status code
def create_json_error_response(message, status):
    response = make_response(json.dumps(message), status)
    response.headers['Content-Type'] = 'application/json'
    return response


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
        'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except NoResultFound:
        return None
    except MultipleResultsFound:
        return None


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        return create_json_error_response('Invalid state parameter.', 401)
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        return create_json_error_response(
            'Failed to upgrade the authorization code.',
            401)

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        return create_json_error_response(result.get('error'), 500)

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        return create_json_error_response(
            "Token's user ID doesn't match given user ID.",
            401)

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        print("Token's client ID does not match app's.")
        return create_json_error_response(
            "Token's client ID does not match app's.",
            401)

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        return create_json_error_response(
            'Current user is already connected.',
            200)

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    user_info = getUserInfo(user_id)
    login_session['is_admin'] = user_info.is_admin

    print("Done!")
    return "Login successful"


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        return create_json_error_response('Current user not connected.', 401)
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        return create_json_error_response('Successfully disconnected.', 200)
    else:
        return create_json_error_response(
            'Failed to revoke token for given user.',
            400)


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['is_admin']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCategories'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCategories'))


# Welcome page after logging in
@app.route('/welcome/')
def showWelcome():
    if 'username' not in login_session:
        return redirect('/login')
    return render_template('welcome.html')


# Landing page - show all categories and recent items
@app.route('/')
@app.route('/catalog/')
def showCategories():
    categories = session.query(Category).order_by(asc(Category.name)).all()
    latestItems = session.query(Item).order_by(desc(Item.id)).limit(10).all()
    return render_template(
        'categories.html',
        categories=categories,
        latestItems=latestItems)


# Create a new category
@app.route('/catalog/category/new/', methods=['GET', 'POST'])
def newCategory():
    if 'username' not in login_session:
        return redirect('/login')
    if login_session.get('is_admin') is not True:
        return render_template('notauthorized.html'), 403
    if request.method == 'POST':
        if request.form['name'] and not request.form['name'].isspace():
            newCategory = Category(
                name=request.form['name'])
            session.add(newCategory)
            session.commit()
            return redirect(url_for('showCategories'))
        else:
            return create_json_error_response("Missing name", 400)
    else:
        return render_template('newcategory.html')


# Edit an existing category
@app.route(
    '/catalog/category/<int:category_id>/edit/',
    methods=['GET', 'POST'])
def editCategory(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    if login_session.get('is_admin') is not True:
        return render_template('notauthorized.html'), 403
    try:
        editedCategory = session.query(
            Category).filter_by(id=category_id).one()
        if request.method == 'POST':
            if request.form['name'] and not request.form['name'].isspace():
                editedCategory.name = request.form['name']
            else:
                return create_json_error_response("Missing name", 400)
            session.add(editedCategory)
            session.commit()
            return redirect(url_for('showCategory', category_id=category_id))
        else:
            return render_template(
                'editcategory.html',
                category=editedCategory)
    except NoResultFound:
        return render_template('notfound.html'), 404
    except MultipleResultsFound:
        return create_json_error_response("More than one category", 409)


# Delete a category
@app.route(
    '/catalog/category/<int:category_id>/delete/',
    methods=['GET', 'POST'])
def deleteCategory(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    if login_session.get('is_admin') is not True:
        return render_template('notauthorized.html'), 403
    try:
        categoryToDelete = session.query(
            Category).filter_by(id=category_id).one()
        if request.method == 'POST':
            session.delete(categoryToDelete)
            session.commit()
            return redirect(url_for('showCategories'))
        else:
            return render_template(
                'deleteCategory.html',
                category=categoryToDelete)
    except NoResultFound:
        return render_template('notfound.html'), 404
    except MultipleResultsFound:
        return create_json_error_response("More than one category", 409)


# Show all items for a given category
@app.route('/catalog/category/<int:category_id>/items/')
def showCategory(category_id):
    categories = session.query(Category).order_by(asc(Category.name)).all()
    category = next(iter(
        [category for category in categories if category.id == category_id]
        or []), None)
    if category is None:
        return render_template('notfound.html'), 404
    items = session.query(Item).filter_by(
        category_id=category_id).order_by(Item.name).all()
    return render_template(
        'category.html',
        categories=categories,
        category=category,
        items=items)


# Show one item
@app.route('/catalog/item/<int:item_id>/')
def showItem(item_id):
    try:
        item = session.query(
            Item).filter_by(id=item_id).one()
        return render_template('item.html', item=item)
    except NoResultFound:
        return render_template('notfound.html'), 404
    except MultipleResultsFound:
        return create_json_error_response("More than one item", 409)


# Add new item to category
@app.route(
    '/catalog/category/<int:category_id>/items/new/',
    methods=['GET', 'POST'])
def newItem(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    # Any logged in user can create an item, so don't check user id
    try:
        category = session.query(
            Category).filter_by(id=category_id).one()
        if request.method == 'POST':
            if request.form['name'] and not request.form['name'].isspace():
                newItem = Item(
                    name=request.form['name'],
                    description=request.form['description'],
                    category_id=category_id,
                    user_id=login_session['user_id'])
                session.add(newItem)
                session.commit()
                return redirect(url_for(
                    'showCategory',
                    category_id=category_id))
            else:
                return create_json_error_response("Missing name", 400)
        else:
            return render_template('newitem.html', category=category)
    except NoResultFound:
        return render_template('notfound.html'), 404
    except MultipleResultsFound:
        return create_json_error_response("More than one item", 409)


# Edit existing item
@app.route('/catalog/item/<int:item_id>/edit/', methods=['GET', 'POST'])
def editItem(item_id):
    if 'username' not in login_session:
        return redirect('/login')
    try:
        item = session.query(Item).filter_by(id=item_id).one()
        categories = session.query(Category).order_by(asc(Category.name)).all()
        if login_session.get('is_admin') is not True and (
                login_session.get('user_id') is None or login_session.get(
                    'user_id') != item.user_id):
            return render_template('notauthorized.html'), 403
        if request.method == 'POST':
            if request.form['name'] and not request.form['name'].isspace():
                item.name = request.form['name']
            else:
                return create_json_error_response("Missing name", 400)
            item.description = request.form['description']
            request_category_id = -1
            try:
                request_category_id = int(request.form['category'])
            except ValueError:
                return create_json_error_response(
                    "Invalid category_id: {}".format(
                        request.form['category']), 400)
            if request_category_id not in \
                    [category.id for category in categories]:
                return create_json_error_response(
                    "category_id does not exist: {}".format(
                        request_category_id), 409)
            item.category_id = request_category_id
            session.add(item)
            session.commit()
            return redirect(url_for(
                'showCategory',
                category_id=item.category_id))
        else:
            return render_template(
                'edititem.html',
                item=item,
                categories=categories)
    except NoResultFound:
        return render_template('notfound.html'), 404
    except MultipleResultsFound:
        return create_json_error_response("More than one item", 409)


# Delete existing item
@app.route('/catalog/item/<int:item_id>/delete/', methods=['GET', 'POST'])
def deleteItem(item_id):
    if 'username' not in login_session:
        return redirect('/login')
    try:
        item = session.query(Item).filter_by(id=item_id).one()
        if login_session.get('is_admin') is not True and (
                login_session.get('user_id') is None or login_session.get(
                    'user_id') != item.user_id):
            return render_template('notauthorized.html'), 403
        if request.method == 'POST':
            session.delete(item)
            session.commit()
            return redirect(url_for(
                'showCategory',
                category_id=item.category_id))
        else:
            return render_template('deleteitem.html', item=item)
    except NoResultFound:
        return render_template('notfound.html'), 404
    except MultipleResultsFound:
        return create_json_error_response("More than one item", 409)


# API endpoint to retrieve all categories
@app.route('/api/catalog/categories/')
def getCategories():
    categories = session.query(Category).all()
    return jsonify(categories=[i.serialize for i in categories])


# API endpoint to retrieve one category
@app.route('/api/catalog/categories/<int:category_id>/')
def getCategory(category_id):
    try:
        category = session.query(Category).filter_by(id=category_id).one()
        return jsonify(category=category.serialize)
    except NoResultFound:
        return render_template('notfound.html'), 404
    except MultipleResultsFound:
        return create_json_error_response("More than one category", 409)


# API endpoint to retrieve one item
@app.route('/api/catalog/items/<int:item_id>/')
def getItem(item_id):
    try:
        item = session.query(Item).filter_by(id=item_id).one()
        return jsonify(item=item.serialize)
    except NoResultFound:
        return render_template('notfound.html'), 404
    except MultipleResultsFound:
        return create_json_error_response("More than one item", 409)


if __name__ == '__main__':
    app.secret_key = json.loads(
        open('app_secrets.json', 'r').read())['app']['app_secret_key']
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
