from flask import Blueprint, render_template, request, redirect, url_for, session
from models import Wines, Reviews, db
from decorators import login_required


bp = Blueprint("wine", __name__)


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

    return render_template("index.html", user=user)


@bp.route("/add_wine", methods=["GET", "POST"])
@login_required
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
@login_required
def get_reviews():
    reviews = Reviews.query.all()
    return render_template("get_reviews.html", reviews=reviews)
