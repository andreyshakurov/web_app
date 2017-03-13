#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, render_template, url_for, request, session, redirect
from flask_pymongo import PyMongo
import bcrypt, os
from datetime import datetime
from momentjs import momentjs


app = Flask(__name__)
app.config['MONGO_HOST'] = os.environ['DB_PORT_27017_TCP_ADDR']
mongo = PyMongo(app, config_prefix='MONGO')
app.jinja_env.globals['momentjs'] = momentjs



@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('profile'))

    return render_template('index.html')


@app.route('/profile')
def profile():
    users = mongo.db.users
    login_user = users.find_one({'name': session['username']})
    name = login_user['name']
    surname = login_user['surname']
    last_seen = login_user['last_seen']
    my_friends = login_user['friend_list']
    city = login_user['city']
    counter = login_user['page_counter']

    return render_template('profile.html', name=name, surname=surname, last_seen=last_seen, my_friends=my_friends, city=city, counter=counter )


@app.route('/add_friends')
def add_friends():
    users = mongo.db.users
    login_user = users.find_one({'name': session['username']})
    all_users = users.distinct('name')
    available_to_add_users = []
    for user in all_users:
        if (user not in login_user['friend_list']) and (user != login_user['name']):
            available_to_add_users.append(user)
    return render_template('add_friends.html', available_to_add_users=available_to_add_users)


@app.route('/add/<new_friend>', methods=['POST', 'GET'])
def add(new_friend):
    if request.method == 'POST':
        users = mongo.db.users
        login_user = users.find_one({'name': session['username']})
        new_friend_user = users.find_one({'name': new_friend})
        my_new_list = list(login_user['friend_list'])
        friends_new_list = list(new_friend_user['friend_list'])
        my_new_list.append(new_friend_user['name'])
        friends_new_list.append(login_user['name'])
        users.update({'name': login_user['name']}, {'$set': {'friend_list': my_new_list}}, upsert=False)
        users.update({'name': new_friend_user['name']}, {'$set': {'friend_list': friends_new_list}}, upsert=False)
    return redirect(url_for('other_user_profile', user=new_friend))

@app.route('/profile/<user>')
def other_user_profile(user):
    users = mongo.db.users
    login_user = users.find_one({'name': session['username']})
    other_user = users.find_one({'name': user})
    if other_user:
        my_name = login_user['name']
        name = other_user['name']
        surname = other_user['surname']
        last_seen = other_user['last_seen']
        my_friends = other_user['friend_list']
        city = other_user['city']
        counter = other_user['page_counter']
        inc_counter = other_user['page_counter'] + 1
        flag_for_adding = name in login_user['friend_list']
        users.update({'name': name}, {'$set': {'page_counter': inc_counter}}, upsert=False)

    return render_template('other_user_profile.html', name=name, surname=surname, last_seen=last_seen, my_friends=my_friends, city=city, counter=counter, my_name=my_name, flag_for_adding=flag_for_adding)


@app.route('/edit_profile', methods=['POST', 'GET'])
def edit_profile():
    users = mongo.db.users
    login_user = users.find_one({'name': session['username']})
    surname = login_user['surname']
    city = login_user['city']
    if request.method == 'POST':
        users.update({'name': login_user['name']}, {'$set': {'surname': request.form['surname'], 'city': request.form['city']}, },   upsert=False)
        return redirect(url_for('profile'))
    return render_template('edit_profile.html', surname=surname, city=city)



@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'name': request.form['username']})
    if login_user:
        if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password'].encode('utf-8')) == login_user['password'].encode('utf-8'):
            session['username'] = request.form['username']
            users.update({'name': login_user['name']}, {'$set': {'last_seen': datetime.utcnow()}}, upsert=False)
            return redirect(url_for('index'))

    return 'Invalid username/password combination'


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        if request.form['username'] and request.form['pass']:
            existing_user = users.find_one({'name': request.form['username']})

            if existing_user is None:
                hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
                users.insert({'name': request.form['username'], 'password': hashpass, 'surname': '', 'city': '', 'last_seen': datetime.utcnow(), 'friend_list': [], 'page_counter': 0 })
                session['username'] = request.form['username']
                return redirect(url_for('index'))

            return 'That username already exists!'
        return 'The fields cannot be empty!'

    return render_template('register.html')

@app.route('/logout')
def logout():
   session.pop('username', None)
   return redirect(url_for('index'))

@app.route('/change_password', methods=['POST', 'GET'])
def change_password():
    if request.method == 'POST':
        users = mongo.db.users

        if request.form['old_pass'] and request.form['new_pass'] and request.form['confirm_new_pass']:
            login_user = users.find_one({'name': session['username']})
            hash_new_pass = bcrypt.hashpw(request.form['new_pass'].encode('utf-8'), bcrypt.gensalt())

            if bcrypt.hashpw(request.form['old_pass'].encode('utf-8'), login_user['password'].encode('utf-8')) == \
                    login_user['password'].encode('utf-8') and (request.form['new_pass'] == request.form['confirm_new_pass']):
                users.update({'name': login_user['name']}, {'$set': {'password': hash_new_pass}}, upsert=False)
                return redirect(url_for('profile'))

            return 'Try once again!'
        return 'The fields cannot be empty!'

    return render_template('change_password.html')

if __name__ == "__main__":
    app.secret_key = os.urandom(24)
    app.run(host='0.0.0.0')
