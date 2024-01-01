from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Wines(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    guest = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    rating = db.Column(db.Integer, nullable=True)

    reviews = db.relationship("Reviews", backref="wine", lazy=True)

    def __repr__(self):
        return f"<Wines id={self.id}, guest={self.guest}, rating={self.rating}>"


class Reviews(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(25), nullable=False)
    wine_id = db.Column(db.Integer, db.ForeignKey("wines.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)

    def __repr__(self):
        return f"<Reviews id={self.id}, user={self.user}, wine={self.wine}, rating={self.rating}>"
