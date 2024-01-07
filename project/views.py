import os
from flask import Blueprint, render_template, request, redirect, url_for, session
from models import Wines, Reviews, db
from decorators import login_required
import pandas as pd
from flask_httpauth import HTTPBasicAuth

poem = """
For Cathy, whose journey's as rich as the sea,
With a heart full of art and history.
In New York's embrace, her story began,
Now she cherishes each day, as only a mother can.

Sam, her star, in West Chester shines bright,
Chasing dreams, reaching new academic heights.
Camille, a Hokie, with a mind keen and vast,
In Doylestown's labs, a Scientist 2, unsurpassed.

Matt strums the guitar, notes floating like a feather,
Teaching young minds, they craft the future together.
In the harmony of strings, in each lesson he weaves,
A tapestry of knowledge, in which every child believes.

Cathy, with a soul that mirrors the ocean's hue,
Finds peace in seashells and the beach's view.
Her spirit, a lighthouse, guiding with care and love,
Illuminating paths for her children, under stars above.

In this family's melody, where love and dreams entwine,
Cathy's artful legacy gracefully continues to shine.
From New York to beaches, where waves gently crest,
In each chapter of life, they are truly blessed.
"""


bp = Blueprint("wine", __name__)

auth = HTTPBasicAuth()

admin_users = {"admin": "bellabites"}  # Replace with your desired username and password


@auth.verify_password
def verify_password(username, password):
    if username in admin_users and admin_users[username] == password:
        return username


@bp.route("/admin")
@auth.login_required
def admin():
    return render_template("admin.html")


@auth.error_handler
def unauthorized():
    return (
        "Unauthorized Access",
        401,
        {"WWW-Authenticate": 'Basic realm="Login Required"'},
    )


@bp.route("/about")
def about():
    return render_template("about.html")


@bp.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user = request.form["user"]
        session["user"] = user  # Set the 'user' session variable
        return redirect(url_for("wine.index"))

    # Check if 'user' exists in the session
    user = session.get("user")
    user_messages = {
        "JOHN": "The Birds at Johns is the best",
        "MATT": "Jack Straw",
        "MIKE": "Welcome Sgt Mike",
        "CATHY": poem,
        "MELISSA": "LOVE YOU FOR DOING THIS AND FOR YOU BEING YOU",
        "LENIN": "YOU WANT TO BREAK THIS APP, BUT WHY, HAVE FUN, ENJOY THE WINE",
        "STEPH": "Hey Doc, give me the pulse of the party",
        "STEPHANIE": "Hey Doc, give me the pulse of the party",
        "BOB": "TALK ABOUT VINTAGE, THATS A 70 YEAR OLD",
        "TINA": "LETS PUFF LATER",
        "CHRISTINA": "LETS PUFF LATER",
        "LAURA": "GAVIN, GRIFFEN, ROSIE...",
        "GINA": "PLEASE DONT JUDGE THESE WINES TOO HARSHLY",
        "REGINA": "PLEASE DONT JUDGE THESE WINES TOO HARSHLY",
        "JUDGE": "PLEASE DONT JUDGE THESE WINES TOO HARSHLY",
        "THE JUDGE": "PLEASE DONT JUDGE THESE WINES TOO HARSHLY",
        "DAN": "OF ALL THE BARS IN BUCKS COUNTY, ISNT THIS HOUSE THE BEST",
        "SCOTT": "WAS THINKING MAYBE POOL LATER BUT WOULD PROBABLY BE A SLOPPY MESS",
    }

    if user is not None:
        message = message = user_messages.get(user.upper(), "")
    else:
        message = ""
    return render_template("index.html", user=user, message=message)


@bp.route("/add_wine", methods=["GET", "POST"])
@login_required
@auth.login_required
def add_wine():
    if request.method == "POST":
        guest = request.form["guest"]
        name = request.form["wine_name"]
        wine = Wines(guest=guest, name=name)
        db.session.add(wine)
        db.session.commit()
        return redirect(url_for("wine.get_wines"))
    return render_template("add_wine.html")


@bp.route("/wines")
@auth.login_required
@login_required
def get_wines():
    wines = Wines.query.all()
    return render_template("wines.html", wines=wines)


@bp.route("/add_review/<id>", methods=["GET", "POST"])
@login_required
def add_review(id):
    max_id = db.session.query(db.func.max(Wines.id)).scalar()
    id = int(id)
    user = session["user"]

    # Check if the user has already submitted a review for this wine
    existing_review = Reviews.query.filter_by(wine_id=id, user=user).first()

    if request.method == "POST":
        if existing_review:
            # User has already submitted a review, perhaps update it instead
            existing_review.rating = request.form["rating"]
            existing_review.notes = request.form["notes"]
        else:
            # Add a new review
            rating = request.form["rating"]
            notes = request.form["notes"]
            review = Reviews(wine_id=id, user=user, rating=rating, notes=notes)
            db.session.add(review)

        db.session.commit()

        # Handling the next and previous buttons
        action = request.form["action"]
        if max_id is not None and action == "Next":
            id = min(id + 1, max_id)
        elif action == "Previous" and id > 1:
            id = id - 1

        return redirect(url_for("wine.add_review", id=id))

    # Pass the existing review to the template, if it exists
    return render_template("add_review.html", id=id, review=existing_review)


@bp.route("/get_reviews")
@auth.login_required
@login_required
def get_reviews():
    reviews = Reviews.query.all()
    return render_template("get_reviews.html", reviews=reviews)


@bp.route("/leaderboard")
@auth.login_required
def leaderboard():
    reviews = pd.read_sql_table("reviews", db.engine)[["wine_id", "rating"]].rename(
        columns={"wine_id": "id"}
    )
    wines = pd.read_sql_table("wines", db.engine)

    df = wines[["id", "guest", "name"]].merge(reviews, on="id", how="left")
    # Compute average ratings and sort
    leaderboard_df = (
        df.groupby(["id", "guest", "name"])["rating"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
        .set_index("id")
    )

    # Style the DataFrame
    styled_df = leaderboard_df.style.set_properties(
        **{
            "text-align": "left",
        }
    ).set_table_styles(
        [
            {"selector": "th", "props": [("text-align", "left")]},
            # Add more styling as needed
        ]
    )

    # Convert to HTML
    leaderboard_html = styled_df.to_html()

    return render_template("leaderboard.html", leaderboard=leaderboard_html)


@bp.route("/reviewer_awards")
@auth.login_required
def reviewer_awards():
    reviews = pd.read_sql_table("reviews", db.engine)
    user_mean = (
        reviews.groupby("user")["rating"]
        .agg(["mean", "std"])
        .sort_values(by="mean")
        .reset_index()
    )

    harshest = user_mean.head(1).to_html(index=False)
    most_generous = user_mean.tail(1).to_html(index=False)
    most_consistant = user_mean.sort_values(by="std").head(1).to_html(index=False)
    return render_template(
        "reviewer_awards.html",
        harshest=harshest,
        most_generous=most_generous,
        most_consistant=most_consistant,
    )
