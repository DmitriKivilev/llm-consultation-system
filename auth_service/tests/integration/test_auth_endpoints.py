import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.main import app
from app.db.base import Base
from app.api.deps import get_db

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(TEST_DATABASE_URL)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

async def override_get_db():
    async with TestSessionLocal() as session:
        yield session

@pytest.fixture(autouse=True)
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def client():
    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

class TestAuthEndpoints:
    async def test_register_user(self, client):
        response = await client.post("/auth/register", json={"email": "test@example.com", "password": "testpass123"})
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert "password_hash" not in data
    
    async def test_register_duplicate(self, client):
        await client.post("/auth/register", json={"email": "test@example.com", "password": "testpass123"})
        response = await client.post("/auth/register", json={"email": "test@example.com", "password": "testpass456"})
        assert response.status_code == 409
    
    async def test_login_success(self, client):
        await client.post("/auth/register", json={"email": "test@example.com", "password": "testpass123"})
        response = await client.post("/auth/login", data={"username": "test@example.com", "password": "testpass123"})
        assert response.status_code == 200
        assert "access_token" in response.json()
    
    async def test_login_wrong_password(self, client):
        await client.post("/auth/register", json={"email": "test@example.com", "password": "testpass123"})
        response = await client.post("/auth/login", data={"username": "test@example.com", "password": "wrongpassword"})
        assert response.status_code == 401
    
    async def test_me_with_valid_token(self, client):
        await client.post("/auth/register", json={"email": "test@example.com", "password": "testpass123"})
        login_resp = await client.post("/auth/login", data={"username": "test@example.com", "password": "testpass123"})
        token = login_resp.json()["access_token"]
        response = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert response.json()["email"] == "test@example.com"
    
    async def test_me_without_token(self, client):
        response = await client.get("/auth/me", headers={})
        assert response.status_code in [401, 403, 422]
