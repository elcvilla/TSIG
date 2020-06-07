import os
import traceback

from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy import func
from shapely.geometry.point import Point

from models import db, Users
from utils import serialize_trajectory

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://docker:docker@db:5432/mobilitydb'
db.init_app(app)
CORS(app)

DATA_UNINITIALIZED_ERROR = "Error a conectar con BD"

def _filter_users_criteria(filters):
    try:
        users = db.session.query(
            Users.userid,
            Users.userpos,
            func.length(Users.userpos),
            func.twAvg(func.speed(Users.userpos))
        ).filter(
            *filters,
        ).all()
    except:
        traceback.print_exc()
        return jsonify({"errors": [DATA_UNINITIALIZED_ERROR]}), 400

    return jsonify({
        "users": [
            {
                "id": user_id,
                "trajectory": serialize_trajectory(user),
                "distance": distance,
                "speed": speed,
            }
            for user_id, user, distance, speed in users
        ]
    })

@app.route('/vetapp/getAll')
def all_users():
    return _filter_users_criteria([])


@app.route('/vetapp/get_trips_by_spatial_query')
def trips_by_spatial_query():
    lat = float(request.args.get("lat"))
    lng = float(request.args.get("lng"))

    return _filter_users_criteria([
        func.intersects(Point(lat, lng).buffer(0.01).wkb, Users.userpos),
    ])

@app.route('/vetapp/ping')
def ping():
    return "OK"
