import asyncio
import httpx
from app.infra.celery_app import celery_app
from app.core.config import settings


@celery_app.task(name="llm_request")
def llm_request(tg_chat_id: int, prompt: str):
    """Обработка запроса к LLM через Celery."""
    
    async def _process():
        # Запрос к OpenRouter
        headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "HTTP-Referer": settings.OPENROUTER_SITE_URL,
            "X-Title": settings.OPENROUTER_APP_NAME,
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": settings.OPENROUTER_MODEL,
            "messages": [
                {"role": "system", "content": "Ты - полезный ассистент. Отвечай на русском языке, кратко и по делу."},
                {"role": "user", "content": prompt}
            ],
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{settings.OPENROUTER_BASE_URL}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            answer = data["choices"][0]["message"]["content"]
        
        # Отправка ответа в Telegram через HTTP API
        bot_token = settings.TELEGRAM_BOT_TOKEN
        send_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            await client.post(send_url, json={
                "chat_id": tg_chat_id,
                "text": answer
            })
        
        return answer
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(_process())
        return result
    finally:
        loop.close()
