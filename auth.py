"""Authentication and authorization for API."""

import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security
security = HTTPBearer()


class TokenData(BaseModel):
    """Token data model."""
    user_id: str
    api_key: Optional[str] = None


class APIKey(BaseModel):
    """API key model."""
    key: str
    user_id: str
    name: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool = True


# In-memory storage (use database in production)
api_keys_db = {}
users_db = {}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> TokenData:
    """Decode and verify a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        return TokenData(user_id=user_id)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )


def verify_api_key(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """Verify API key from Authorization header."""
    token = credentials.credentials
    
    # Check if it's an API key
    if token.startswith("sk-"):
        if token in api_keys_db:
            api_key = api_keys_db[token]
            if api_key.is_active:
                # Check expiration
                if api_key.expires_at and api_key.expires_at < datetime.utcnow():
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="API key has expired"
                    )
                return api_key.user_id
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    # Otherwise treat as JWT token
    token_data = decode_access_token(token)
    return token_data.user_id


def create_api_key(user_id: str, name: str, expires_days: Optional[int] = None) -> str:
    """Create a new API key for a user."""
    import secrets
    
    # Generate secure random key
    key = f"sk-{secrets.token_urlsafe(32)}"
    
    expires_at = None
    if expires_days:
        expires_at = datetime.utcnow() + timedelta(days=expires_days)
    
    api_key = APIKey(
        key=key,
        user_id=user_id,
        name=name,
        created_at=datetime.utcnow(),
        expires_at=expires_at,
        is_active=True
    )
    
    api_keys_db[key] = api_key
    return key


def revoke_api_key(key: str) -> bool:
    """Revoke an API key."""
    if key in api_keys_db:
        api_keys_db[key].is_active = False
        return True
    return False


def list_user_api_keys(user_id: str) -> list:
    """List all API keys for a user."""
    return [
        {
            "key": key[:10] + "..." + key[-4:],
            "name": api_key.name,
            "created_at": api_key.created_at.isoformat(),
            "expires_at": api_key.expires_at.isoformat() if api_key.expires_at else None,
            "is_active": api_key.is_active
        }
        for key, api_key in api_keys_db.items()
        if api_key.user_id == user_id
    ]
