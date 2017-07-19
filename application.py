#!/usr/bin/env python2.7
from database_setup import Base, Category, User, Item
from flask import Flask, render_template, request, redirect, url_for, flash
from flask import jsonify, session as login_session, make_response
import httplib2
import json
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import random
import requests
import string
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = 'Item Catalog Application'

engine = create_engine('postgresql:///catalog')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return 'The current session state is %s' % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps('Token\'s user ID doesn\'t match given user ID.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps('Token\'s client ID does not match app\'s.'), 401)
        print 'Token\'s client ID does not match app\'s.'
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.to_json()
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['access_token'] = credentials.access_token
    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash('You are now logged in as %s!' % login_session['username'])
    print 'done!'
    return output


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.user_id


def getUserInfo(user_id):
    user = session.query(User).filter_by(user_id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.user_id
    except:
        return None


def getLoggedInUser():
    if 'user_id' not in login_session:
        return None
    else:
        return login_session['user_id']


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['access_token']
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    if access_token is None:
        print 'Access Token is None'
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s'
    url = url % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash('Successfully disconnected.')
        return redirect(url_for('Categories'))
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/catalog/JSON')
def catalogJSON():
    categories = session.query(Category).all()
    cat_list = [cat.serialize for cat in categories]
    for cat in cat_list:
        items = session.query(Item).filter_by(cat_id=cat['cat_id']).all()
        cat['items'] = [i.serialize for i in items]
    return jsonify(cat_list)


@app.route('/')
def Categories():
    categories = session.query(Category).all()
    latest = session.query(Item).order_by(Item.date_added.desc()).limit(10)
    return render_template('home.html', categories=categories, latest=latest,
                           current_user_id=getLoggedInUser())


@app.route('/categories/<int:cat_id>/items')
def listCategoryItems(cat_id):
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(cat_id=cat_id).one()
    items = session.query(Item).filter_by(cat_id=cat_id).all()
    return render_template('items.html', categories=categories,
                           category=category, items=items,
                           current_user_id=getLoggedInUser())


@app.route('/items/<int:item_id>')
def getItemDetails(item_id):
    item = session.query(Item).filter_by(item_id=item_id).one()
    return render_template('item.html', item=item,
                           current_user_id=getLoggedInUser())


def loginRedirect():
    flash('You must login to view this page!')
    return redirect('/login')


@app.route('/catalog/new', methods=['GET', 'POST'])
def newItem():
    if 'username' not in login_session:
        return loginRedirect()
    if request.method == 'POST':
        item = Item(title=request.form['title'], description=request.form[
                    'description'], cat_id=request.form['category'],
                    user_id=login_session['user_id'])
        session.add(item)
        session.commit()
        flash('New item created!')
        return redirect(url_for('Categories'))
    else:
        categories = session.query(Category).all()
        return render_template('newitem.html', categories=categories,
                               current_user_id=getLoggedInUser())


@app.route('/items/<int:item_id>/edit', methods=['GET', 'POST'])
def editItem(item_id):
    if 'username' not in login_session:
        return loginRedirect()
    item = session.query(Item).filter_by(item_id=item_id).one()
    if item.user_id != getLoggedInUser():
        flash('You can only edit items that you created.')
        return redirect(url_for('Categories'))
    categories = session.query(Category).all()
    if request.method == 'POST':
        if request.form['title']:
            item.title = request.form['title']
        if request.form['description']:
            item.description = request.form['description']
        if request.form['category']:
            item.cat_id = request.form['category']
        session.add(item)
        session.commit()
        flash('Item has been edited!')
        return redirect(url_for('getItemDetails', item_id=item_id))
    else:
        return render_template('edititem.html', item=item,
                               categories=categories,
                               current_user_id=getLoggedInUser())


@app.route('/items/<int:item_id>/delete', methods=['GET', 'POST'])
def deleteItem(item_id):
    if 'username' not in login_session:
        return loginRedirect()
    item = session.query(Item).filter_by(item_id=item_id).one()
    if item.user_id != getLoggedInUser():
        flash('You can only delete items that you created.')
        return redirect(url_for('Categories'))
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        flash('Item has been deleted!')
        return redirect(url_for('Categories'))
    else:
        return render_template('deleteitem.html', item=item,
                               current_user_id=getLoggedInUser())


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
