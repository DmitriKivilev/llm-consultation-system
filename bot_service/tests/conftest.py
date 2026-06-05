import pytest
from fakeredis import FakeAsyncRedis


@pytest.fixture
async def fake_redis(monkeypatch):
    """Подменяем реальный Redis на fake."""
    fake_redis_client = FakeAsyncRedis(decode_responses=True)
    
    async def mock_get_redis():
        return fake_redis_client
    
    monkeypatch.setattr("app.bot.handlers.get_redis", mock_get_redis)
    
    yield fake_redis_client
    
    await fake_redis_client.flushall()
