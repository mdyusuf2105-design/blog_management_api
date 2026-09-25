from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import User
from auth0 import get_auth0_user

router = APIRouter(
    prefix="/auth",
    tags=["Auth0 Authentication"]
)


@router.get("/callback")
def auth0_callback(
    current_user: User = Depends(get_auth0_user),
):
    return {
        "message": "Auth0 authentication successful",
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
        }
    }