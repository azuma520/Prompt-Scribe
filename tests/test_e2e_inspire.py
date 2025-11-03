import os
import pytest
import httpx


def _has_env() -> bool:
    return bool(os.getenv("OPENAI_API_KEY") and os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_ANON_KEY"))


@pytest.mark.anyio
@pytest.mark.e2e
async def test_inspire_e2e_start_status_continue():
    if not _has_env():
        pytest.skip("Missing required env for E2E: OPENAI_API_KEY, SUPABASE_URL, SUPABASE_ANON_KEY")

    base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    async with httpx.AsyncClient(base_url=base_url, timeout=30.0) as ac:
        # 1) start
        start_payload = {"message": "櫻花樹下的和服少女，溫柔寧靜的氛圍", "user_access_level": "all-ages"}
        r = await ac.post("/api/inspire/start", json=start_payload)
        assert r.status_code == 200
        data = r.json()
        assert "session_id" in data and data["session_id"]
        session_id = data["session_id"]

        # 2) status
        r2 = await ac.get(f"/api/inspire/status/{session_id}")
        assert r2.status_code == 200
        s = r2.json()
        assert s.get("metadata", {}).get("current_phase") in {"understanding", "exploring", "refining", "finalizing", "completed"}

        # 3) continue
        cont_payload = {"session_id": session_id, "message": "選擇第 2 個方向"}
        r3 = await ac.post("/api/inspire/continue", json=cont_payload)
        assert r3.status_code in (200, 400)
        body = r3.json()
        assert "message" in body or body.get("error") in {"content_unsafe", "aborted"}


