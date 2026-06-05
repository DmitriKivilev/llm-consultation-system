import pytest
from unittest.mock import AsyncMock
from datetime import datetime, timedelta
from jose import jwt
from aiogram.types import Message, User, Chat
from app.core.config import settings
from app.bot.handlers import cmd_token, handle_message


@pytest.fixture
def mock_message():
    message = AsyncMock(spec=Message)
    message.from_user = User(id=12345, is_bot=False, first_name="Test")
    message.chat = Chat(id=12345, type="private")
    message.answer = AsyncMock()
    return message


def create_test_token(user_id="123", role="user"):
    payload = {
        "sub": user_id,
        "role": role,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(minutes=60)
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)


class TestTokenCommand:
    @pytest.mark.asyncio
    async def test_save_valid_token(self, mock_message, fake_redis):
        token = create_test_token()
        mock_message.text = f"/token {token}"
        
        await cmd_token(mock_message)
        
        saved_token = await fake_redis.get(f"token:{mock_message.from_user.id}")
        assert saved_token == token
        
        mock_message.answer.assert_called_once()
        args = mock_message.answer.call_args[0][0]
        assert "Токен успешно сохранен" in args
    
    @pytest.mark.asyncio
    async def test_save_invalid_token(self, mock_message, fake_redis):
        mock_message.text = "/token invalid_token"
        
        await cmd_token(mock_message)
        
        saved_token = await fake_redis.get(f"token:{mock_message.from_user.id}")
        assert saved_token is None
        
        mock_message.answer.assert_called_once()
        args = mock_message.answer.call_args[0][0]
        assert "Ошибка" in args or "проблема" in args


class TestMessageHandler:
    @pytest.mark.asyncio
    async def test_message_without_token(self, mock_message, fake_redis):
        mock_message.text = "Hello LLM"
        
        await handle_message(mock_message)
        
        mock_message.answer.assert_called_once()
        args = mock_message.answer.call_args[0][0]
        assert "необходима авторизация" in args
    
    @pytest.mark.asyncio
    async def test_message_with_valid_token(self, mock_message, fake_redis, mocker):
        token = create_test_token()
        await fake_redis.setex(f"token:{mock_message.from_user.id}", 3600, token)
        
        mock_message.text = "Hello LLM"
        
        # Мокаем импорт llm_request внутри функции handle_message
        mock_delay = mocker.patch("app.tasks.llm_tasks.llm_request.delay")
        mock_delay.return_value.id = "test-task-id"
        
        await handle_message(mock_message)
        
        mock_delay.assert_called_once_with(
            tg_chat_id=mock_message.chat.id,
            prompt="Hello LLM"
        )
        
        mock_message.answer.assert_called_once()
        args = mock_message.answer.call_args[0][0]
        assert "запрос принят" in args
