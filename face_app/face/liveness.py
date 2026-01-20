import numpy as np
def dist(p1, p2):
    p1 = np.array(p1)
    p2 = np.array(p2)
    return np.linalg.norm(p1 - p2)


def ear_left_eye(lm):
    h = dist(lm[33], lm[35])
    v1 = dist(lm[36], lm[41])
    v2 = dist(lm[37], lm[42])
    v3 = dist(lm[40], lm[33])
    return (v1 + v2 + v3) / (3 * h + 1e-6)

def ear_right_eye(lm):
    h = dist(lm[89], lm[93])
    v1 = dist(lm[90], lm[95])
    v2 = dist(lm[91], lm[96])
    v3 = dist(lm[94], lm[87])
    return (v1 + v2 + v3) / (3 * h + 1e-6)

def eye_open_close(landmark, ear_th):
    ear_l = ear_left_eye(landmark)
    ear_r = ear_right_eye(landmark)
    is_left_open = ear_l >= ear_th
    is_right_open = ear_r >= ear_th
    return is_left_open, is_right_open