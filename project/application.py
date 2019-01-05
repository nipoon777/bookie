import os
import requests
import json

from cs50 import SQL
from flask import Flask, flash, render_template, url_for, request, session, \
    redirect,jsonify
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import *


# configure application

app = Flask(__name__)


# ensure responses aren't cached

if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, \
                                            must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response




# configure the session to use filesystem
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

#Start the Session
Session(app)


# configure the database system
db = SQL("sqlite:///books.db")


@app.route("/")
@login_required
def index():

    results = db.execute("SELECT * FROM books")

    return render_template("index.html",results = results)



@app.route("/register", methods =["GET","POST"])
def register():

    # clear the session

    session.clear()

    if request.method == "POST":
        # Check whether the User has full filled all the required conditions
        if not request.form.get("username"):
            return render_template("error.html",message ="please provide username")
        elif not request.form.get("password"):
            return render_template("error.html",message ="please provide password")
        elif request.form.get("password") != request.form.get("confirmation"):
            return render_template("error.html", message ="password does not match")

        # if all the conditions are satisfied insert into the users table
        result = db.execute("INSERT INTO users(username,hash) VALUES (:username,:hash)",\
        username = request.form.get("username"), hash = generate_password_hash(request.form.get("password")))

        if not result :
            return render_template("error.html", message ="USER EXISTS ALREADY")
        session["user_id"]= result
        return redirect(url_for("login"))
    else:

        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    # forget any user_id
    session.clear()
    # if the user reached the route via (by submitting the form via POST request)

    if request.method == "POST":

        # ensure that username is submitted
        if not request.form.get("username"):
            return render_template("error.html", message ="PLEASE provide the username")

        # ensure that password is entered
        elif not request.form.get("password"):
            return render_template("error.html", message ="Please enter the password")
        # Query the database

        row = db.execute("SELECT * FROM users WHERE username = :username",\
        username = request.form.get("username"))

        if len(row)!= 1 or not check_password_hash(row[0]["hash"],request.form.get("password")):
            return render_template("error.html",message = "Incorrect username/password")

        session["user_id"] = row[0]["username"]

        return redirect("/")

    else:
        return render_template("login.html")


@app.route("/search", methods =["GET","POST"])
@login_required
def search():
    s = "%" + request.form.get("search") + "%"

    rows = db.execute("SELECT * FROM books WHERE title LIKE :s OR author LIKE :s OR isbn LIKE :s",s=s)

    if  not rows:

        return render_template("error.html", message = "Sorry, no record found")
    else:
        return render_template("search.html", rows=rows)

@app.route("/review/<book_id>",methods =["GET","POST"])
@login_required
def review(book_id):
    b_id = book_id

    if request.method == "POST" :

        result = db.execute("SELECT * FROM reviews WHERE author = :user AND book_id = :id",
        user=session["user_id"], id = b_id )

        userreview = result

        if not userreview:
            # Get all data from submitted form
            rating = request.form.get("rating")
            review_text = request.form.get("review_text")

            # add review to database
            db.execute("INSERT INTO reviews (book_id, author, rating, review_text) VALUES (:book_id, :author, :rating, :review_text)",
            book_id = b_id,  author = session["user_id"], rating = rating, review_text = review_text)


            # Make URL to redirect user back to updated book-page
            this_book_url = "/review/" + b_id

            # redirect user to updated book page
            return redirect(this_book_url)
        else:
            # If already reviewed render error page
            return render_template("error.html",message ="You already reviewed this book.")


    else:

        result = db.execute("SELECT * FROM books WHERE book_id =:book_id", book_id = b_id)

        for row in result:
            book_data = dict(row)

        book_data['book_id'] = b_id

        review_result  = get_review_count(book_data['isbn'])

        book_data['average_rating'] = review_result['average_rating']
        book_data['number_ratings'] = review_result['number_ratings']
        # Get all reviews on this book from reviews table
        result = db.execute("SELECT author, rating, review_text FROM reviews WHERE book_id = :id",
                            id = b_id)

        # Store all rows in a list of dicts
        review_rows = []

        for row in result:
            review_rows.append(dict(row))


        return render_template("review.html",book_data = book_data, review_rows = review_rows)

@app.route("/logout")
def logout():

    # clear the session

    session.clear()

    return redirect(url_for("login"))

@app.route("/api/<isbn>")
def api(isbn):
    # allow the user to acces the data using the API key
    isbn = isbn


    result = db.execute("SELECT title, author, year, isbn FROM books WHERE isbn = :isbn ", isbn = isbn)

    if not result:
        return render_template("error.html", message = "not found")
    for row in result:
        book_data = dict(row)

    review_result = get_review_count(book_data['isbn'])

    book_data['average_rating'] = review_result['average_rating']
    book_data['number_ratings'] = review_result['number_ratings']

    book_json = json.dumps(book_data)

    return book_json






