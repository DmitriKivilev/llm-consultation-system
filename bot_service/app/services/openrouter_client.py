import httpx
from app.core.config import settings


class OpenRouterClient:
    """Клиент для взаимодействия с OpenRouter API."""
    
    def __init__(self):
        self._base_url = settings.OPENROUTER_BASE_URL
        self._api_key = settings.OPENROUTER_API_KEY
        self._model = settings.OPENROUTER_MODEL
        self._site_url = settings.OPENROUTER_SITE_URL
        self._app_name = settings.OPENROUTER_APP_NAME

    async def send_message(self, prompt: str) -> str:
        """
        Отправляет запрос к LLM и возвращает ответ.
        """
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "HTTP-Referer": self._site_url,
            "X-Title": self._app_name,
            "Content-Type": "application/json",
        }

        payload = {
            "model": self._model,
            "messages": [{"role": "user", "content": prompt}],
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{self._base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                
                if "choices" in data and len(data["choices"]) > 0:
                    return data["choices"][0]["message"]["content"]
                else:
                    return "Error: No response from model"
                    
            except httpx.HTTPStatusError as e:
                raise Exception(f"OpenRouter API error: {e.response.status_code}")
            except Exception as e:
                raise Exception(f"OpenRouter connection error: {str(e)}")
