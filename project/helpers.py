import csv
import os
import urllib.request
import requests

from flask import redirect, render_template, request, session
from functools import wraps


# So as to allow only the authentic user to access the data

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


# Query the GOODREADS api to access the ratings and count through isbn number
def get_review_count(isbn):

    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "PANh14GvLTygsXvxHHNAw", "isbns": isbn })
    json_data = res.json()

    average_rating = json_data['books'][0]['average_rating']
    number_ratings = json_data['books'][0]['work_reviews_count']

    if not average_rating:
        return "NOT FOUND"
    if not number_ratings:
        return "NOT FOUND"

    result_review_count = { 'average_rating' : average_rating , 'number_ratings' : number_ratings }

    return result_review_count

