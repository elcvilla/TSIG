import trajectory
from datetime import datetime
from flask import Flask, jsonify

def serialize_trajectory(user):
    #print(user)
    a = []
    for p in user.reset_index().values.tolist():
        a.append(datetime.fromtimestamp(p[0].timestamp()).strftime("%Y-%m-%dT%H:%M:%SZ"))
        a.append(p[1].x)
        a.append(p[1].y)
        a.append(0)

    return ({
            "epoch": a[0],
            "cartographicDegrees": a
        })

'''
    return trajectory.encode([
        (p[1].x, p[1].y, p[0].timestamp())
        for p in user.reset_index().values.tolist()
    ])
'''
'''
      "cartographicDegrees":[
        0,-56.189652081027,-34.8988227843656,0,
        100,-56.189652081027,-34.8888227843656,0,
		150,-56.189652081027,-34.8888227843656,0,
        200,-56.189652081027,-34.8988227843656,0,
        300,-56.189652081027,-34.8888227843656,0
      ]
'''
