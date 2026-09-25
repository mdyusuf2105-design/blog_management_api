import os

import requests
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
from dotenv import load_dotenv

from database import get_db
from models import User

load_dotenv()

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_AUDIENCE = os.getenv("AUTH0_AUDIENCE")

security = HTTPBearer()


def get_auth0_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db=Depends(get_db),
):
    token = credentials.credentials

    if not AUTH0_DOMAIN or not AUTH0_AUDIENCE:
        raise HTTPException(
            status_code=500,
            detail="Auth0 configuration is missing"
        )

    try:
        issuer = f"https://{AUTH0_DOMAIN}/"

        jwks_url = f"{issuer}.well-known/jwks.json"

        jwks = requests.get(jwks_url, timeout=10)

        if not jwks.ok:
            raise HTTPException(
                status_code=500,
                detail="Unable to retrieve Auth0 signing keys"
            )

        jwks = jwks.json()

        unverified_header = jwt.get_unverified_header(token)

        rsa_key = {}

        for key in jwks["keys"]:
            if key["kid"] == unverified_header.get("kid"):
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"],
                }
                break

        if not rsa_key:
            print("AUTH0 TOKEN KID:", unverified_header.get("kid"))
            print("AUTH0 JWKS KIDS:", [key.get("kid") for key in jwks.get("keys", [])])

            raise HTTPException(
                status_code=401,
                detail="Invalid Auth0 token"
            )

        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            audience=AUTH0_AUDIENCE,
            issuer=issuer,
        )

        email = payload.get("https://blog-management-api/email") or payload.get("email")
        name = payload.get("name") or payload.get("nickname")

        if not email:
            raise HTTPException(
                status_code=400,
                detail="Email not provided by Auth0"
            )

        user = db.query(User).filter(User.email == email).first()

        if not user:
            user = User(
                username=name or email.split("@")[0],
                email=email,
                password="AUTH0_USER",
            )

            db.add(user)
            db.commit()
            db.refresh(user)

        return user

    except HTTPException:
        raise

    except Exception as e:
        print("AUTH0 VALIDATION ERROR:", repr(e))
        raise HTTPException(
            status_code=401,
            detail="Invalid Auth0 token"
        )