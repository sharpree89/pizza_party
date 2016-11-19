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
    return render_template('index.html')

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
        return redirect('/pizza')
    else:
        flash("There were errors registering the user.")
        return redirect('/')

@app.route('/login', methods=['POST'])
def login():
    # if form data passes validations:
    if len(request.form['username']) > 5 and len(request.form['password']) > 7:
        user_query = "SELECT * FROM users WHERE username = :username LIMIT 1"
        query_data = { 'username': request.form['username'] }
        user = mysql.query_db(user_query, query_data) # user will be returned in a list

        if bcrypt.check_password_hash(user[0]['pw_hash'], request.form['password']):
            session["user"] = user[0]
            return redirect('/pizza')
        else:
            flash("Incorrect login info - try again!")
            return redirect('/')
    else:
        flash("Incorrect login info - try again!")
        return redirect('/')

#-------------------------------------------------------------------------------
# CREATING AND STORING PIZZA

@app.route('/pizza')
def pizza():
    toppings = []
    session["toppings"] = toppings
    return render_template('index.html')

@app.route('/add', methods=['POST'])
def addToppings():
    if request.method == "POST":
        session["toppings"].append(request.form['topping'])
    return render_template('index.html')

@app.route('/done')
def createPizza():

    if len(session["toppings"]) == 0:
        flash("You haven't added any toppings yet!")
        return redirect('/pizza')
    else:
        toppings_string = ', '.join(session["toppings"])
        query = "INSERT INTO pizzas (toppings, created_at, updated_at, user_id) VALUES (:toppings, NOW(), NOW(), :user_id)"
        # We'll then create a dictionary of data from the POST data received.
        data = {
                 'toppings': toppings_string,
                 'user_id': session["user"]["id"]
               }
        # Run query, with dictionary values injected into the query.
        mysql.query_db(query, data)

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
