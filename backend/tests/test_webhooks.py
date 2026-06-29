import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_webhook_verification():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/webhooks/whatsapp?hub.mode=subscribe&hub.challenge=1158201444&hub.verify_token=mavve_secret_token_123")
    assert response.status_code == 200
    assert response.text == "1158201444"

@pytest.mark.asyncio
async def test_webhook_invalid_token():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/webhooks/whatsapp?hub.mode=subscribe&hub.challenge=1158201444&hub.verify_token=wrong_token")
    assert response.status_code == 403
