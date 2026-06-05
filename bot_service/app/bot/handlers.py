from aiogram import Router, types
from aiogram.filters import Command
from app.infra.redis import get_redis
from app.core.jwt import decode_and_validate

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Добро пожаловать в LLM-консультант!\n\n"
        "Для начала работы необходимо авторизоваться:\n"
        "1. Получите JWT токен через Auth Service\n"
        "2. Отправьте его командой /token ваш_токен\n\n"
        "После этого вы сможете задавать вопросы LLM."
    )


@router.message(Command("token"))
async def cmd_token(message: types.Message):
    try:
        token = message.text.split(" ", 1)[1] if " " in message.text else None
        
        if not token:
            await message.answer("Укажите токен: /token ваш_jwt_токен")
            return
        
        try:
            payload = decode_and_validate(token)
            user_id = payload.get("sub")
            role = payload.get("role", "user")
        except ValueError as e:
            await message.answer(f"Ошибка: {str(e)}")
            return
        
        redis = await get_redis()
        tg_user_id = message.from_user.id
        await redis.setex(f"token:{tg_user_id}", 3600, token)
        
        await message.answer(
            f"Токен успешно сохранен!\n"
            f"User ID: {user_id}\n"
            f"Role: {role}\n\n"
            f"Теперь вы можете задавать вопросы LLM."
        )
        
    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}")


@router.message()
async def handle_message(message: types.Message):
    try:
        tg_user_id = message.from_user.id
        
        redis = await get_redis()
        token = await redis.get(f"token:{tg_user_id}")
        
        if not token:
            await message.answer(
                "Для использования бота необходима авторизация.\n"
                "Получите JWT токен через Auth Service и отправьте его командой:\n"
                "/token ваш_jwt_токен"
            )
            return
        
        try:
            decode_and_validate(token)
        except ValueError as e:
            await message.answer(
                f"Ваш токен недействителен: {str(e)}\n"
                "Получите новый токен и отправьте его /token токен"
            )
            await redis.delete(f"token:{tg_user_id}")
            return
        
        from app.tasks.llm_tasks import llm_request
        
        task = llm_request.delay(
            tg_chat_id=message.chat.id,
            prompt=message.text
        )
        
        await message.answer(
            f"Ваш запрос принят и обрабатывается...\n"
            f"Task ID: {task.id}"
        )
        
    except Exception as e:
        await message.answer(f"Произошла ошибка: {str(e)}")
