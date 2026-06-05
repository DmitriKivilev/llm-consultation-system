from fastapi import Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.repositories.users import UserRepository
from app.usecases.auth import AuthUseCase
from app.core.security import decode_token
from app.core.exceptions import InvalidTokenError, TokenExpiredError

security = HTTPBearer(description="Вставьте ваш токен")


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


async def get_users_repo(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


async def get_auth_uc(user_repo: UserRepository = Depends(get_users_repo)) -> AuthUseCase:
    return AuthUseCase(user_repo)


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = credentials.credentials
    try:
        payload = decode_token(token)
        return payload
    except ValueError as e:
        if "expired" in str(e).lower():
            raise TokenExpiredError()
        raise InvalidTokenError()
