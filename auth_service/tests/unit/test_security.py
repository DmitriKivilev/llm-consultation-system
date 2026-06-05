import pytest
from app.core.security import hash_password, verify_password, create_access_token, decode_token


class TestPasswordHashing:
    
    def test_hash_is_different_from_password(self):
        password = "testpassword123"
        hashed = hash_password(password)
        assert hashed != password
    
    def test_verify_correct_password(self):
        password = "testpassword123"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True
    
    def test_verify_incorrect_password(self):
        password = "testpassword123"
        hashed = hash_password(password)
        assert verify_password("wrongpassword", hashed) is False


class TestJWT:
    
    def test_create_and_decode_token(self):
        data = {"sub": "1", "role": "user"}
        token = create_access_token(data)
        payload = decode_token(token)
        
        assert payload["sub"] == "1"
        assert payload["role"] == "user"
        assert "iat" in payload
        assert "exp" in payload
    
    def test_decode_invalid_token(self):
        with pytest.raises(ValueError):
            decode_token("invalid.token.here")
