from jose import jwt, JWTError
from .config import settings


def decode_and_validate(token: str) -> dict:
    """
    Проверяет JWT токен: подпись, срок действия.
    Возвращает payload или выбрасывает исключение.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except JWTError:
        raise ValueError("Invalid token")
