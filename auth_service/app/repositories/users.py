from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models import User


class UserRepository:
    """Репозиторий для работы с пользователями."""
    
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_email(self, email: str) -> User | None:
        """Получить пользователя по email."""
        result = await self._session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> User | None:
        """Получить пользователя по id."""
        result = await self._session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(self, email: str, password_hash: str) -> User:
        """Создать нового пользователя."""
        user = User(email=email, password_hash=password_hash)
        self._session.add(user)
        await self._session.commit()
        await self._session.refresh(user)
        return user
