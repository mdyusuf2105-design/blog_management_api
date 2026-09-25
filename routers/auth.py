from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import get_db
from models import User, SubscriptionPlan
from schemas import UserCreate, UserResponse, Token
from auth import hash_password, verify_password, create_access_token


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# =========================
# REGISTER / SIGNUP
# =========================
@router.post("/register", response_model=UserResponse)
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    # Check username
    existing_user = db.query(User).filter(
        User.username == user.username
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )

    # Check email
    existing_email = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Find Basic subscription plan
    basic_plan = db.query(SubscriptionPlan).filter(
        SubscriptionPlan.name == "Basic"
    ).first()

    if not basic_plan:
        raise HTTPException(
            status_code=500,
            detail="Basic subscription plan not found"
        )

    # Hash password
    hashed_password = hash_password(user.password)

    # Create user
    new_user = User(
        username=user.username,
        email=user.email,
        password=hashed_password,
        subscription_plan_id=basic_plan.id,
        subscription_start=None,
        subscription_end=None
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# =========================
# LOGIN
# =========================
@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # The OAuth2 "username" field is used here to enter EMAIL.
    existing_user = db.query(User).filter(
        User.email == form_data.username.strip()
    ).first()

    if not existing_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Verify password
    if not verify_password(
        form_data.password,
        existing_user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Create JWT access token
    access_token = create_access_token(
        data={
            "sub": str(existing_user.id)
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/signup", response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(
        User.username == user.username
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )

    existing_email = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    basic_plan = db.query(SubscriptionPlan).filter(
        SubscriptionPlan.name == "Basic"
    ).first()

    if not basic_plan:
        raise HTTPException(
            status_code=500,
            detail="Basic subscription plan not found"
        )

    hashed_password = hash_password(user.password)

    new_user = User(
        username=user.username,
        email=user.email,
        password=hashed_password,
        subscription_plan_id=basic_plan.id,
        subscription_start=None,
        subscription_end=None
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user