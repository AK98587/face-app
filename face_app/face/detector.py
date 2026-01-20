import numpy as np

def normalize_emb(emb):
    emb = emb.astype(np.float32)
    norm = np.linalg.norm(emb)
    if norm < 1e-6:
        return None
    return emb / norm

def extract_faces_frsom_image(img, app):
    faces = app.get(img)
    face_records = []

    for face in faces:
        # 1. Chuẩn hóa embedding
        emb = normalize_emb(face.embedding)
        if emb is None:
            continue

        # 2. Lấy Landmark 106 (kiểm tra nếu mô hình có hỗ trợ)
        # Nếu app được load với 2d106det, nó sẽ nằm trong landmark_2d_106
        lmk106 = None
        if hasattr(face, 'landmark_2d_106'):
            lmk106 = face.landmark_2d_106.astype(float).tolist()
        # 3. Xây dựng bản ghi
        face_records.append({
            "bbox": face.bbox.tolist(),
            "emb": emb.tolist(),
            "score": float(face.det_score),
            "pose": face.pose.tolist() if hasattr(face.pose, 'tolist') else face.pose,
            "landmark106": lmk106,
        })

    return face_records