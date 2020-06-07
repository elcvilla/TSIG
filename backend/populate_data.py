import csv
import datetime
from collections import defaultdict

import pandas as pd
from shapely.geometry import Point

from main import app
from models import db, Users


users_data = defaultdict(list)

with open("go_track_trackspoints.csv") as csvfile:
    csvreader = csv.reader(csvfile)
    first_row = True
    for row in csvreader:
        if first_row:
            first_row = False
            continue

        user_id, lat, lng, time = int(row[3]), float(row[1]), float(row[2]), datetime.datetime.strptime(row[4], '%Y-%m-%d %H:%M:%S')
        users_data[user_id].append({"geometry": Point(lat, lng), "t": time})

with app.app_context():
    #db.drop_all()
    #db.create_all()

    print("Trying to populate {} rows".format(len(users_data)))

    for userid in users_data:
        try:
            print("Trying ....")
            df = pd.DataFrame(users_data[userid]).set_index("t")
            user = Users(userid=userid, userpos=df,)
            db.session.add(user)
            db.session.commit()
        except:
            print("Couldn't save Users #{} of length {}".format(user_id, len(users_data[user_id])))
