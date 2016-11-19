from flask import Flask, render_template, request, redirect, session, flash
from random import randint
app = Flask(__name__)
app.secret_key = "supersecret"

@app.route('/')
def index():

    currentOrder = ""
    session["currentOrder"] = currentOrder
    if len(session["currentOrder"]) == 0:
        session["currentOrder"] = ""

    return render_template('index.html')

@app.route('/add', methods=['POST'])
def addToppings():

    if request.method == "POST":
        session["currentOrder"] += request.form['topping'] + " "
        print session["currentOrder"]

    return render_template('index.html')

@app.route('/done')
def placeOrder():

    if len(session["currentOrder"]) == 0:
        flash("You haven't added any toppings yet!")
        return redirect('/')
    else:
        return render_template('done.html')

@app.route('/reset')
def reset():

    session.clear()
    return redirect('/')

app.run(debug=True)
