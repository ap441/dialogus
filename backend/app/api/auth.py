from fastapi import APIRouter, Depends, HTTPException, status
from google.auth.transport import requests
from google.oauth2 import id_token
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password, verify_password, create_access_token
from app.db.session import get_db
from app.deps import get_current_user
from app.models import User
from app.schemas import SignupRequest, LoginRequest, GoogleTokenRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/signup", response_model=TokenResponse)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    exists = db.query(User).filter(User.email == payload.email).first()
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already in use")

    user = User(
        full_name=payload.full_name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.commit()

    token = create_access_token(user.email)
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(user.email)
    return TokenResponse(access_token=token)


@router.post("/google", response_model=TokenResponse)
def google_login(payload: GoogleTokenRequest, db: Session = Depends(get_db)):
    if not settings.google_client_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Google OAuth not configured")

    try:
        # Verify the Google ID token
        id_info = id_token.verify_oauth2_token(
            payload.token, requests.Request(), settings.google_client_id
        )

        email = id_info.get("email")
        full_name = id_info.get("name", email.split("@")[0])

        if not email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")

        # Find or create user
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(
                full_name=full_name,
                email=email,
                hashed_password=hash_password(""),  # Google-authenticated users don't need password
            )
            db.add(user)
            db.commit()

        token = create_access_token(user.email)
        return TokenResponse(access_token=token)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid Google token: {str(e)}")


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user
