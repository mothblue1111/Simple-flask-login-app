import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ. get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")


mongo = PyMongo(app)

"""
Design wise, improvement to the overall user experience and navigation
    - Comments page can be public
Display comments done by user on their profile
    - They can press on edit/delete on any comment
    - This will redirect them to an edit comment page
Make sure that people who didn't write the comment cannot edit it as well (check the username of the comment and the user logged in, if logged in)
Comments displayed can be nicer in terms of design
You can also have an image (file/url) of the barber saved in the db
Clean up the db
Add proper function comments throughout and function documentation
It would be beneficial if you used the contact form you have in forms.py and add an endpoint to handle a "dummy" send email.
README file
"""


def is_logged_in():
    return session.get('user')


@app.route("/")
@app.route("/get_home")
def get_home():
    """
    List variable is reviews
    """
    categories = list(mongo.db.categories.find())
    reviews = get_reviews()
    return render_template("reviews.html", categories=categories, reviews=reviews)


@app.route("/")
@app.route("/contact")
def contact():
    """
    Accepts both GET and POST and implement with the ContactForm and it should just print out the message from the user.
    print(request.form['message'])
    """
    categories = list(mongo.db.categories.find())
    reviews = get_reviews()
    return render_template("reviews.html", categories=categories, reviews=reviews)


@app.route("/add_review", methods=["GET", "POST"])
def add_review():
    """
    To post scomment of text in form(revicommentsubmitted)
    """
    if is_logged_in():
        # user is logged in
        if request.method == "POST":
            # handle post
            review_data = {
                'barber_name': request.form['barber_name'],
                'comment': request.form['comment'],
                'date_of_cut': request.form['date_of_cut'],
                'author': session['user'],
            }
            print(review_data)
            new_record_id = mongo.db.reviews.insert_one(review_data)
            flash("Created comment successfully", "success")
            return redirect(url_for("get_reviews"))

        # get request
        return render_template("add_review.html")

    flash("Register or log in", "warning")
    return redirect(url_for("register"))


@app.route("/get_reviews")
def get_reviews():
    reviews = list(mongo.db.reviews.find())
    return render_template("comments.html", reviews=reviews)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in mongodb
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}".format(
                    request.form.get("username")))
                return redirect(url_for(
                    "profile", username=session["user"]))
            else:
                # password invalid
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # username does not exist
            flash("OH NO! Username and/or password does not exist")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile", methods=["GET", "POST"])
def profile():
    # grab the session user's username from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        reviews = mongo.db.reviews.find({"author": username})
    return render_template("profile.html", review=reviews)
    return redirect(url_for("login"))



@app.route("/logout")
def logout():
    # remove user from session cookie
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/edit_review", methods=["GET", "POST"])
def edit_review():
    # grab the session user's username from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        reviews = mongo.db.reviews.find({"author"})
        return render_template("edit_review.html", get_reviews=reviews)

if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
