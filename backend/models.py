from flask_sqlalchemy import SQLAlchemy
from mobilitydb_sqlalchemy import TGeomPoint

db = SQLAlchemy()


class Users(db.Model):
    __tablename__ = "users"
    userid = db.Column(db.Integer, primary_key=True)
    userpos = db.Column(TGeomPoint)
