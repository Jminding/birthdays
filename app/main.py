import os
from sqlalchemy import create_engine
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from datetime import date as dt
from dotenv import load_dotenv

load_dotenv()

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DB_URI")

# Configure sqlalchemy to use birthdays
db = create_engine(os.getenv("DB_URI"))


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # TODO: Add the user's entry into the database
        error = ""
        name = request.form.get("name")
        date = request.form.get("date")
        if not name:
            error = "Missing name!"
        elif not date:
            error = "Missing date!"
        else:
            month, day, year = date.split("-")[1], date.split("-")[2], date.split("-")[0]
            names = list(db.execute("SELECT name FROM birthdays"))
            names = [i[0] for i in names]
            age = dt.today().year - int(year)
            if int(month) > dt.today().month or (int(month) == dt.today().month and int(day) > dt.today().day):
                    age -= 1
            if name in names:
                db.execute(
                    f"""
                    UPDATE birthdays
                    SET month = {month}, day = {day}, year = {year}, age = {age}
                    WHERE name = '{name}'
                    """
                )
                error = "Updated birthday."
            else:
                db.execute(
                    """
                    INSERT INTO birthdays (name, month, day, year, age) VALUES(?, ?, ?, ?, ?)
                    """,
                    name,
                    month,
                    day,
                    year,
                    age,
                )
                error = "Added birthday!"
        birthdays = db.execute("SELECT * FROM birthdays")
        return render_template("index.html", message=error, birthdays=birthdays)

    else:

        # TODO: Display the entries in the database on index.html
        birthdays = db.execute("SELECT * FROM birthdays")
        return render_template("index.html", birthdays=birthdays)

if __name__ == "__main__":
    app.run()

