# Face Authentication Backend (FastAPI)

Hệ thống backend xác thực người dùng bằng **khuôn mặt đa góc nhìn (5 pose)**, xây dựng bằng **FastAPI + MongoDB (Motor)**, hỗ trợ:

* Đăng ký tài khoản
* Thu thập 5 ảnh khuôn mặt theo pose
* Xác thực khuôn mặt lại (face verify) theo đúng logic đăng ký
* JWT Access Token / Refresh Token

---

## 1. Tổng quan kiến trúc

### Công nghệ sử dụng

* **FastAPI** – REST API
* **MongoDB + Motor** – Database async
* **JWT** – xác thực người dùng
* **OpenCV** – xử lý ảnh
* **Face Embedding Model** – trích xuất vector khuôn mặt

---

## 2. Quy ước 5 loại khuôn mặt (Pose)

Hệ thống **bắt buộc đúng 5 pose sau**:

```text
FRONT
LEFT
RIGHT
LOOK_UP
LOOK_DOWN
```

* Không yêu cầu upload theo thứ tự
* Backend tự kiểm tra pose bằng góc mặt (pitch, yaw)
* Mỗi pose **chỉ được upload 1 lần**

---

## 3. Flow nghiệp vụ tổng thể

### 🔐 Authentication

1. `/auth/token` – Login → nhận access & refresh token
2. `/auth/refresh` – refresh access token

### 📝 Đăng ký (Register)

1. `/auth/register/init`
2. `/auth/register/face` (5 lần – mỗi lần 1 ảnh)
3. `/auth/register/finalize`

### ✅ Xác thực khuôn mặt (Verify)

1. `/auth/face-verify/face` (5 lần – giống đăng ký)
2. `/auth/face-verify/finalize`

---

## 4. API chi tiết

### 4.1 Login

`POST /auth/token`

Body (JSON):

```json
{
  "email": "user@email.com",
  "password": "password"
}
```

Response:

```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer"
}
```

---

### 4.2 Register – Khởi tạo

`POST /auth/register/init`

Form-data:

* `user_name`
* `email`
* `password`

Response:

```json
{
  "message": "User initialized",
  "user_id": "...",
  "required_faces": ["FRONT","LEFT","RIGHT","LOOK_UP","LOOK_DOWN"]
}
```

---

### 4.3 Register – Upload face

`POST /auth/register/face`

Headers:

```
Authorization: Bearer <access_token>
```

Form-data:

* `face_type` (FRONT | LEFT | ...)
* `face_file` (image)

Response:

```json
{
  "uploaded": "LEFT",
  "missing_faces": ["FRONT","RIGHT","LOOK_UP","LOOK_DOWN"],
  "completed": false
}
```

---

### 4.4 Register – Finalize

`POST /auth/register/finalize`

Headers:

```
Authorization: Bearer <access_token>
```

Response:

```json
{
  "message": "User registered successfully"
}
```

Sau bước này user có `status = ACTIVE`

---

## 5. Face Verify (xác thực lại)

### 5.1 Upload verify face

`POST /auth/face-verify/face`

Headers:

```
Authorization: Bearer <access_token>
```

Form-data:

* `face_type`
* `face_file`

Response:

```json
{
  "uploaded": "FRONT",
  "missing_faces": ["LEFT","RIGHT","LOOK_UP","LOOK_DOWN"],
  "completed": false
}
```

> Verify flow **giống 100% register**, nhưng lưu vào `verify_faces`

---

### 5.2 Finalize verify

`POST /auth/face-verify/finalize`

Headers:

```
Authorization: Bearer <access_token>
```

Logic:

* So sánh **từng pose** verify với pose đăng ký
* Tính cosine similarity
* Lấy **điểm trung bình 5 ảnh**

Response (success):

```json
{
  "message": "Face verified successfully",
  "avg_score": 0.73
}
```

Response (fail):

```json
{
  "message": "Face verification failed",
  "avg_score": 0.42,
  "scores": {
    "FRONT": 0.5,
    "LEFT": 0.4,
    "RIGHT": 0.39,
    "LOOK_UP": 0.45,
    "LOOK_DOWN": 0.36
  }
}
```

---

## 6. Pose check logic (cốt lõi)

```python
if pitch > 15:
    return "LOOK_UP"
elif pitch < -15:
    return "LOOK_DOWN"

if abs(yaw) < 20:
    return "FRONT"
elif yaw > 20:
    return "LEFT"
else:
    return "RIGHT"
```

Backend **không tin frontend**, luôn tự kiểm tra pose.

---

## 7. Lưu ý quan trọng

* ❌ Không gửi đủ 5 ảnh → không finalize
* ❌ Sai pose → reject
* ❌ Thiếu token → `Not authenticated`
* ❌ Không dùng `await` với Mongo async → crash

---

## 8. Gợi ý cải tiến (optional)

* Redis cache thay vì lưu `verify_faces` trong DB
* Anti-spoof nâng cao (blink, depth)
* Rate limit verify
* Audit log mỗi lần verify

---

## 9. Kết luận

✔ Register và Verify **dùng cùng logic**
✔ Không phụ thuộc thứ tự upload
✔ Bảo mật bằng JWT
✔ Dễ mở rộng production

---

📌 Tác giả: *Face Authentication System*
