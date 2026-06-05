import pytest
import respx
from httpx import Response
from app.services.openrouter_client import OpenRouterClient
from app.core.config import settings


class TestOpenRouterClient:
    @pytest.mark.asyncio
    async def test_send_message_success(self):
        test_response = "Это тестовый ответ от LLM"
        
        with respx.mock:
            respx.post(f"{settings.OPENROUTER_BASE_URL}/chat/completions").mock(
                return_value=Response(200, json={
                    "choices": [{
                        "message": {
                            "content": test_response
                        }
                    }]
                })
            )
            
            client = OpenRouterClient()
            result = await client.send_message("Тестовый запрос")
            
            assert result == test_response
    
    @pytest.mark.asyncio
    async def test_send_message_http_error(self):
        with respx.mock:
            respx.post(f"{settings.OPENROUTER_BASE_URL}/chat/completions").mock(
                return_value=Response(500, json={"error": "Internal Server Error"})
            )
            
            client = OpenRouterClient()
            
            with pytest.raises(Exception, match="OpenRouter API error"):
                await client.send_message("Тестовый запрос")
