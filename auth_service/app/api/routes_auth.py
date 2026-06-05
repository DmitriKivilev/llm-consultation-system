from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import get_auth_uc, get_current_user
from app.usecases.auth import AuthUseCase
from app.schemas.auth import RegisterRequest, TokenResponse
from app.schemas.user import UserPublic

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserPublic)
async def register(
    request: RegisterRequest,
    usecase: AuthUseCase = Depends(get_auth_uc),
):
    """Регистрация нового пользователя."""
    return await usecase.register(email=request.email, password=request.password)


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    usecase: AuthUseCase = Depends(get_auth_uc),
):
    """Вход пользователя и получение JWT."""
    return await usecase.login(email=form_data.username, password=form_data.password)


@router.get("/me", response_model=UserPublic)
async def me(
    payload: dict = Depends(get_current_user),
    usecase: AuthUseCase = Depends(get_auth_uc),
):
    """Получение профиля текущего пользователя."""
    user_id = int(payload.get("sub"))
    return await usecase.me(user_id=user_id)
