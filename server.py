from flask import Flask, redirect, render_template, request, session, flash
from mysqlconnection import MySQLConnector
from flask.ext.bcrypt import Bcrypt
from random import randint

app = Flask(__name__)
app.secret_key = "supersecretkey!"
mysql = MySQLConnector(app, 'mydb')
bcrypt = Bcrypt(app)

#-------------------------------------------------------------------------------
# REGISTRATION & LOGIN

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    # if form data passes validations:
    if len(request.form['username']) > 5 and len(request.form['password']) > 7 and request.form['password'] == request.form['confirm_password']:
        # hash the pw before storing it in the db.
        pw_hash = bcrypt.generate_password_hash(request.form["password"])
        query = "INSERT INTO users (username, pw_hash, created_at, updated_at) VALUES (:username, :pw_hash, NOW(), NOW())"
        # We'll then create a dictionary of data from the POST data received.
        data = {
                 'username': request.form['username'],
                 'pw_hash': pw_hash
               }
        # Run query, with dictionary values injected into the query.
        mysql.query_db(query, data)

        # store user info in session
        user_query = "SELECT * FROM users WHERE username = :username LIMIT 1"
        query_data = { 'username': request.form['username'] }
        user = mysql.query_db(user_query, query_data) # user will be returned in a list

        session["userid"] = user[0]["id"]
        session["username"] = user[0]["username"]

        return redirect('/pizza')
    else:
        return redirect('/signup')

@app.route('/login', methods=['POST'])
def login():
    # if form data passes validations:
    if len(request.form['username']) > 5 and len(request.form['password']) > 7:
        user_query = "SELECT * FROM users WHERE username = :username LIMIT 1"
        query_data = { 'username': request.form['username'] }
        user = mysql.query_db(user_query, query_data) # user will be returned in a list

        if bcrypt.check_password_hash(user[0]['pw_hash'], request.form['password']):
            session["userid"] = user[0]["id"]
            session["username"] = user[0]["username"]
            return redirect('/pizza')
        else:
            return redirect('/')
    else:
        return redirect('/')

#-------------------------------------------------------------------------------
# CREATING AND STORING PIZZA

@app.route('/pizza')
def pizza():

    session['toppings'] = []
    return render_template('index.html')

@app.route('/add', methods=['POST'])
def addToppings():

    session['toppings'] = request.form.getlist('topping')
    print session['toppings']

    if len(session['toppings']) == 0:
        flash("You haven't added any toppings yet!")
        return redirect('/pizza')
    else:
        query = "INSERT INTO pizzas (toppings, created_at, updated_at, user_id) VALUES (:toppings, NOW(), NOW(), :user_id)"
        # We'll then create a dictionary of data from the POST data received.
        toppings_string = ', '.join(session['toppings'])
        session['display_toppings'] = toppings_string
        data = {
                 'toppings': toppings_string,
                 'user_id': session["userid"]
               }
        # Run query, with dictionary values injected into the query.
        mysql.query_db(query, data)

        new_query = "SELECT * FROM pizzas"
        pizzas = mysql.query_db(new_query)
        pizza_count = len(pizzas)
        session['pizza_count'] = pizza_count

        return redirect('/done')

@app.route('/done')
def createPizza():


    return render_template('done.html')

#-------------------------------------------------------------------------------

@app.route('/reset')
def reset():

    session["toppings"] = []
    return redirect('/pizza')

@app.route('/logout')
def logout():

    session.clear()

    return redirect('/')

#-------------------------------------------------------------------------------
# DELETING A USER, PIZZA, OR RATING

# @app.route('/delete/<user_id>', methods=['POST'])
# def deleteUser(user_id):
#     query = "DELETE FROM users WHERE id = :id"
#     data = {'id': user_id}
#     mysql.query_db(query, data)
#     return redirect('/pizza')
#
# @app.route('/delete/<pizza_id>', methods=['POST'])
# def deletePizza(pizza_id):
#     query = "DELETE FROM pizzas WHERE id = :id"
#     data = {'id': pizza_id}
#     mysql.query_db(query, data)
#     return redirect('/pizza')
#
# @app.route('/delete/<rating_id>', methods=['POST'])
# def deleteRating(rating_id):
#     query = "DELETE FROM ratings WHERE id = :id"
#     data = {'id': rating_id}
#     mysql.query_db(query, data)
#     return redirect('/pizza')

app.run(debug=True)
