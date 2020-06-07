import trajectory


def serialize_trajectory(user):
    return trajectory.encode([
        (p[1].x, p[1].y, p[0].timestamp())
        for p in user.reset_index().values.tolist()
    ])
