def face_angle_state(pose):
    pitch, yaw, roll = pose


    if pitch > 15:
        states = "LOOK_UP"
    elif pitch < -15:
        states = "LOOK_DOWN"

    elif abs(yaw) < 20:
        states = "FRONT"
    elif yaw > 20:
        states = "LEFT"
    else:
        states = "RIGHT"

    return states
