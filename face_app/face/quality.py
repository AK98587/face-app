import cv2
import numpy as np

def crop_face_with_scale(img, bbox, scale=1.3):
    """
    Crop face image from bbox with scale (margin)

    Args:
        img (np.ndarray): original image (H, W, C)
        bbox (list | tuple | np.ndarray): [x1, y1, x2, y2]
        scale (float): expand ratio (1.2 ~ 1.5 recommended)

    Returns:
        face_crop (np.ndarray): cropped face image
    """

    h, w = img.shape[:2]
    x1, y1, x2, y2 = map(int, bbox)

    bw = x2 - x1
    bh = y2 - y1

    # center of bbox
    cx = x1 + bw // 2
    cy = y1 + bh // 2

    # scaled size
    new_bw = int(bw * scale)
    new_bh = int(bh * scale)

    # new bbox
    nx1 = max(0, cx - new_bw // 2)
    ny1 = max(0, cy - new_bh // 2)
    nx2 = min(w, cx + new_bw // 2)
    ny2 = min(h, cy + new_bh // 2)

    face_crop = img[ny1:ny2, nx1:nx2].copy()

    return face_crop


def is_blurry(img,bbox, thresh=80):
    face_crop = crop_face_with_scale(img, bbox)
    gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
    blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
    return blur_score < thresh, blur_score
def brightness_ok(img,bbox, min_val=60, max_val=200):
    face_crop = crop_face_with_scale(img, bbox)
    gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
    mean = gray.mean()
    return min_val <= mean <= max_val, mean
def size_ok(bbox, min_size=80):
    x1, y1, x2, y2 = map(int, bbox)
    width = x2 - x1
    height = y2 - y1
    return width >= min_size and height >= min_size, (width, height)