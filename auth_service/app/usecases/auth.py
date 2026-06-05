from app.repositories.users import UserRepository
from app.core.security import hash_password, verify_password, create_access_token
from app.core.exceptions import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
    UserNotFoundError,
)
from app.schemas.user import UserPublic
from app.schemas.auth import TokenResponse


class AuthUseCase:
    """Бизнес-логика аутентификации."""
    
    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo

    async def register(self, email: str, password: str) -> UserPublic:
        """Регистрация нового пользователя."""
        existing_user = await self._user_repo.get_by_email(email)
        if existing_user:
            raise UserAlreadyExistsError()
        
        password_hash = hash_password(password)
        user = await self._user_repo.create(email=email, password_hash=password_hash)
        return UserPublic.model_validate(user)

    async def login(self, email: str, password: str) -> TokenResponse:
        """Вход пользователя и выдача JWT."""
        user = await self._user_repo.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise InvalidCredentialsError()
        
        token_data = {"sub": str(user.id), "role": user.role}
        access_token = create_access_token(token_data)
        return TokenResponse(access_token=access_token)

    async def me(self, user_id: int) -> UserPublic:
        """Получить профиль пользователя."""
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        return UserPublic.model_validate(user)
