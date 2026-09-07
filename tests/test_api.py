import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from backend.api.main import app
from backend.core.shared import app_state
from backend.core.state import VpnState

@pytest.mark.asyncio
async def test_concurrent_api_access():
    app_state.set_state(VpnState.ANALYZING)
    
    # httpx 0.28 requires ASGITransport
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create 50 concurrent requests
        tasks = []
        for _ in range(25):
            tasks.append(client.get("/health"))
            tasks.append(client.get("/status"))
            
        responses = await asyncio.gather(*tasks)
        
        # Verify no crashes or errors
        for r in responses:
            assert r.status_code == 200
            
        # Verify JSON validity
        health_responses = [r.json() for r in responses if "capture" in r.json()]
        status_responses = [r.json() for r in responses if "state" in r.json() and "capture" not in r.json()]
        
        assert len(health_responses) > 0
        assert len(status_responses) > 0
        assert health_responses[0]["state"] == "ANALYZING"
