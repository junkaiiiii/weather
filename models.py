from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class City(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable = False, unique = True)

    def __repr__(self):
        return f"<City: {self.name} >"
    