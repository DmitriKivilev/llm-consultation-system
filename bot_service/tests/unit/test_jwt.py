import pytest
from datetime import datetime, timedelta
from jose import jwt
from app.core.jwt import decode_and_validate
from app.core.config import settings


class TestJWTValidation:
    def test_decode_valid_token(self):
        payload = {
            "sub": "123",
            "role": "user",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(minutes=60)
        }
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
        decoded = decode_and_validate(token)
        assert decoded["sub"] == "123"
        assert decoded["role"] == "user"
    
    def test_decode_invalid_token(self):
        with pytest.raises(ValueError, match="Invalid token"):
            decode_and_validate("invalid.token.here")
    
    def test_decode_expired_token(self):
        payload = {
            "sub": "123",
            "role": "user",
            "iat": datetime.utcnow() - timedelta(hours=2),
            "exp": datetime.utcnow() - timedelta(hours=1)
        }
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
        with pytest.raises(ValueError, match="Token has expired"):
            decode_and_validate(token)
