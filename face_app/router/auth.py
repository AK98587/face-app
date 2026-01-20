from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException
from fastapi import Header
from datetime import timedelta
from bson import ObjectId
from datetime import datetime
from face_app.face.embedding import cosine_similarity
from face_app.core.security import (
    get_current_user,
    verify_password,
    create_access_token,
    get_password_hash,
    decode_token,
    create_refresh_token
)
from face_app.core.database import get_db
from face_app.services.face_services import FaceService
from face_app.schemas.user_schemas import UserLogin
from fastapi import Form, File, UploadFile
import numpy as np
import cv2
from typing import List
from face_app.models.users_model import user_model

router = APIRouter(prefix="/auth", tags=["Auth"])

FACE_VERIFY_THRESHOLD = 0.5

REQUIRED_FACE_TYPES = {
    "FRONT",
    "LEFT",
    "RIGHT",
    "LOOK_UP",
    "LOOK_DOWN"
}


from fastapi.security import OAuth2PasswordRequestForm

@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db = Depends(get_db)
):
    user = await db.users.find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(401, "Invalid email or password")

    payload = {"id": str(user["_id"])}

    return {
        "access_token": create_access_token(payload, timedelta(minutes=30)),
        "refresh_token": create_refresh_token(payload),
        "token_type": "bearer"
    }

@router.post("/refresh")
async def refresh_access_token(
    refresh_token: str = Header(...),
    db = Depends(get_db)
):
    payload = decode_token(refresh_token)

    # 1Check đúng loại refresh token
    if payload.get("sub") != "refresh":
        raise HTTPException(401, "Invalid refresh token")

    user_id = payload.get("id")
    if not user_id:
        raise HTTPException(401, "Invalid token payload")

    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(401, "User not found")

    # Cấp access token mới
    new_access_token = create_access_token(
        payload={"id": user_id},
        expires=timedelta(minutes=30)
    )

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }
@router.post("/register/init")
async def register_init(
    user_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db = Depends(get_db)
):
    if await db.users.find_one({"email": email}):
        raise HTTPException(400, "Email already exists")

    user = {
        "user_name": user_name,
        "email": email,
        "password_hash": get_password_hash(password),
        "status": "PENDING",
        "face_embeddings": {},   # chưa có ảnh
        "created_at": datetime.utcnow()
    }

    result = await db.users.insert_one(user)

    return {
        "message": "User initialized",
        "user_id": str(result.inserted_id),
        "required_faces": list(REQUIRED_FACE_TYPES)
    }


@router.post("/register/face")
async def upload_face(
    user_id: str = Form(...),
    face_type: str = Form(...),
    face_file: UploadFile = File(...),
    db = Depends(get_db)
):
    user = await db.users.find_one({"_id": ObjectId(user_id)})

    face_type = face_type.upper().strip()

    if face_type not in REQUIRED_FACE_TYPES:
        raise HTTPException(400, f"Invalid face_type: {face_type}")

    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(404, "User not found")

    if user["status"] != "PENDING":
        raise HTTPException(400, "User already finalized")

    if face_type in user["face_embeddings"]:
        raise HTTPException(400, f"{face_type} already uploaded")

    # ==== xử lý ảnh ====
    contents = await face_file.read()
    img_array = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    if img is None:
        raise HTTPException(400, "Invalid image")

    face_service = FaceService()

    try:
        result = face_service.process_image(img, face_type)
        face_service.pose_check(result["pose"], face_type)
        face_service.liveness_check(result["lmk106"], face_type)

        emb = result["emb"]
        if emb is None or len(emb) == 0:
            raise HTTPException(400, "No embedding found")

    except ValueError as e:
        raise HTTPException(400, str(e))

    # ==== lưu embedding ====
    await db.users.update_one(
        {"_id": ObjectId(user["_id"])},
        {"$set": {f"face_embeddings.{face_type}": emb}}
    )

    # ==== check còn thiếu ====
    updated_user = await db.users.find_one({"_id": ObjectId(user["_id"])})
    uploaded = set(updated_user["face_embeddings"].keys())
    missing = list(REQUIRED_FACE_TYPES - uploaded)

    return {
        "uploaded": face_type,
        "missing_faces": missing,
        "completed": len(missing) == 0
    }
@router.post("/register/finalize")
async def finalize_register(
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    user = current_user
    if not user:
        raise HTTPException(404, "User not found")

    uploaded = set(user["face_embeddings"].keys())
    if uploaded != REQUIRED_FACE_TYPES:
        raise HTTPException(
            400,
            f"Missing face types: {list(REQUIRED_FACE_TYPES - uploaded)}"
        )

    await db.users.update_one(
        {"_id": ObjectId(user["_id"])},
        {"$set": {"status": "ACTIVE"}}
    )

    return {"message": "User registered successfully"}
@router.post("/face-verify/face")
async def upload_verify_face(
    face_type: str = Form(...),
    face_file: UploadFile = File(...),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    face_type = face_type.upper().strip()

    if face_type not in REQUIRED_FACE_TYPES:
        raise HTTPException(400, "Invalid face_type")

    # lưu tạm vào session verify
    verify_key = f"verify_faces.{face_type}"

    contents = await face_file.read()
    img_array = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    face_service = FaceService()
    result = face_service.process_image(img, face_type)

    face_service.pose_check(result["pose"], face_type)
    face_service.liveness_check(result["lmk106"], face_type)

    emb = result["emb"]

    await db.users.update_one(
        {"_id": current_user["_id"]},
        {"$set": {verify_key: emb}}
    )

    user = await db.users.find_one({"_id": current_user["_id"]})
    uploaded = set(user.get("verify_faces", {}).keys())
    missing = list(REQUIRED_FACE_TYPES - uploaded)

    return {
        "uploaded": face_type,
        "missing_faces": missing,
        "completed": len(missing) == 0
    }
@router.post("/face-verify/finalize")
async def finalize_face_verify(
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    user = current_user

    reg_faces = user["face_embeddings"]
    verify_faces = user.get("verify_faces", {})

    if set(verify_faces.keys()) != REQUIRED_FACE_TYPES:
        raise HTTPException(400, "Not enough verify images")

    scores = []

    for face_type in REQUIRED_FACE_TYPES:
        sim = cosine_similarity(
            verify_faces[face_type],
            reg_faces[face_type]
        )
        scores.append(sim)

    avg_score = sum(scores) / len(scores)

    if avg_score < FACE_VERIFY_THRESHOLD:
        raise HTTPException(
            401,
            {
                "message": "Face verification failed",
                "avg_score": avg_score,
                "scores": dict(zip(REQUIRED_FACE_TYPES, scores))
            }
        )

    # cleanup
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$unset": {"verify_faces": ""}}
    )

    return {
        "message": "Face verified successfully",
        "avg_score": avg_score
    }
