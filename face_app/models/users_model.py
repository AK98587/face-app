from datetime import datetime, timezone


def user_model(
    user_name: str,
    email: str,
    password_hash: str
):
    return {
        "user_name": user_name,
        "email": email,
        "password": password_hash,
        "is_active": True,
        "faces": [],  # embeddings
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
