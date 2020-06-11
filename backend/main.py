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

    # Import the library
    from czml import czml

    # Initialize a document
    doc = czml.CZML()

    # Create and append the document packet
    packet1 = czml.CZMLPacket(id='document',version='1.0')
    doc.packets.append(packet1)

    # Create and append a POINT packet
    packet3 = czml.CZMLPacket()

    for user_id, user, distance, speed in users:
        packet3.id = user_id
        pp = czml.Point()
        pp.color = {'rgba': [0, 255, 127, 55]}
        pp.outlineColor = {'rgba':[255,0,0,128]}

        #varPos = czml.Position(cartographicDegrees=[2020-06-04T16:00:00Z,-56.189652081027,-34.8888227843656,0,2020-06-04T16:05:00Z,-56.189652081027,-34.8888227843656,0])
        pos = czml.Position()
        #coords = ['2020-06-04T16:00:00Z','-56.189652081027','-34.8888227843656','0','2020-06-04T16:05:00Z','-56.189652081027','-34.8888227843656','0']

        coords = serialize_trajectory(user)
        pos.epoch = coords['epoch']
        pos.cartographicDegrees = coords['cartographicDegrees']

        #varPos.cartographicDegrees = [2020-06-04T16:00:00Z,-56.189652081027,-34.8888227843656,0,2020-06-04T16:05:00Z,-56.189652081027,-34.8888227843656,0]

        #trayectoria = Path(pos,pp)
        packet3.position = pos
        packet3.point = pp

        #Path(pos, pp)

        #packet3.path = trayectoria
        #pp.Position = Position(varPos)
        doc.packets.append(packet3)

    # Write the CZML document to a file
    filename = "example.czml"
    doc.write(filename)

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
