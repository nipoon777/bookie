import csv
import os
from cs50 import SQL
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


db = SQL("sqlite:///books.db")


def main():
    f = open("books.csv")

    reader = csv.reader(f)
    for isbn, title, author, year in reader:
        # db.execute("INSERT INTO flights (origin, destination, duration) VALUES (:origin, :destination, :duration)",
            #        {"origin": origin, "destination": destination, "duration": duration})
        db.execute("INSERT INTO books(isbn, title, author, year) VALUES(:isbn, :title,:author, :year)",isbn=isbn, title = title,\
        author=author,year=year)
    db.commit()
    close(f)


if __name__ == "__main__":
    main()
