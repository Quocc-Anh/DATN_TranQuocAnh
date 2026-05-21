import base64
import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.models import User
from app.schemas.auth import (
    PasswordChange,
    TokenResponse,
    UserLogin,
    UserOut,
    UserRegister,
    UserUpdate,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])

AVATAR_DIR = os.path.join("data", "avatars")
os.makedirs(AVATAR_DIR, exist_ok=True)


def _issue_token(user: User) -> TokenResponse:
    token = create_access_token(user.id)
    return TokenResponse(access_token=token, user=UserOut.from_orm(user))


@router.post("/register", response_model=TokenResponse)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email đã được sử dụng")
    user = User(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _issue_token(user)


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Email hoặc mật khẩu không đúng")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Tài khoản đã bị khóa")
    return _issue_token(user)


@router.post("/token", response_model=TokenResponse)
def token_login(
    form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email hoặc mật khẩu không đúng",
        )
    return _issue_token(user)


@router.get("/me", response_model=UserOut)
def me(current: User = Depends(get_current_user)):
    return current


@router.patch("/me", response_model=UserOut)
def update_me(
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    if payload.full_name is not None:
        name = payload.full_name.strip()
        if not name:
            raise HTTPException(status_code=400, detail="Họ tên không được để trống")
        current.full_name = name
    if payload.avatar_url is not None:
        current.avatar_url = payload.avatar_url
    db.commit()
    db.refresh(current)
    return current


@router.post("/me/avatar", response_model=UserOut)
def upload_avatar(
    request: Request,
    payload: dict,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    """Nhận avatar dạng base64 (gọn cho mobile). Body: {'image_base64': '...', 'ext': 'jpg'}"""
    b64 = payload.get("image_base64")
    ext = (payload.get("ext") or "jpg").lower().strip(".")
    if not b64 or ext not in {"jpg", "jpeg", "png", "webp"}:
        raise HTTPException(status_code=400, detail="Ảnh không hợp lệ")
    try:
        raw = base64.b64decode(b64)
    except Exception:
        raise HTTPException(status_code=400, detail="Base64 sai định dạng")
    if len(raw) > 3 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Ảnh quá lớn (tối đa 3MB)")
    filename = f"{current.id}_{uuid.uuid4().hex[:8]}.{ext}"
    path = os.path.join(AVATAR_DIR, filename)
    with open(path, "wb") as f:
        f.write(raw)
    base = str(request.base_url).rstrip("/")
    current.avatar_url = f"{base}/uploads/avatars/{filename}"
    db.commit()
    db.refresh(current)
    return current


@router.post("/me/password", response_model=UserOut)
def change_password(
    payload: PasswordChange,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    if not verify_password(payload.current_password, current.hashed_password):
        raise HTTPException(status_code=400, detail="Mật khẩu hiện tại không đúng")
    if len(payload.new_password) < 6:
        raise HTTPException(status_code=400, detail="Mật khẩu mới phải tối thiểu 6 ký tự")
    current.hashed_password = hash_password(payload.new_password)
    db.commit()
    db.refresh(current)
    return current
