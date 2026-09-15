
from fastapi.testclient import TestClient

from backend.main import app
from backend.knowledge_base import search_sources


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_empty_message():
    response = client.post(
        "/chat",
        json={
            "message": "",
            "mode": "chat",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Message cannot be empty."


def test_invalid_mode():
    response = client.post(
        "/chat",
        json={
            "message": "What is product-market fit?",
            "mode": "invalid",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Mode must be either 'chat' or 'essay'."
    )


def test_knowledge_base_search():
    results = search_sources("product-market fit")

    assert isinstance(results, list)


def test_llm_failure(monkeypatch):
    async def fake_ask_llm(prompt):
        raise RuntimeError("LLM unavailable")

    monkeypatch.setattr(
        "backend.agent.ask_llm",
        fake_ask_llm,
    )

    response = client.post(
        "/chat",
        json={
            "message": "What is product-market fit?",
            "mode": "chat",
        },
    )

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "The growth assistant is currently unavailable."
    )


def test_provider_in_response(monkeypatch):
    async def fake_ask_llm(prompt):
        return "Test answer"

    monkeypatch.setattr(
        "backend.agent.ask_llm",
        fake_ask_llm,
    )

    response = client.post(
        "/chat",
        json={
            "message": "What is growth?",
            "mode": "chat",
        },
    )

    assert response.status_code == 200
    assert response.json()["provider"] == "ollama"


def test_retrieval_returns_source_fields():
    results = search_sources("product-market fit")

    assert isinstance(results, list)

    if results:
        source = results[0]

        assert "id" in source
        assert "title" in source
        assert "content" in source
        assert "url" in source


def test_conversation_persistence(monkeypatch):
    async def fake_ask_llm(prompt):
        return "Test answer"

    monkeypatch.setattr(
        "backend.agent.ask_llm",
        fake_ask_llm,
    )

    session_id = "persistence-test-session"

    first_response = client.post(
        "/chat",
        json={
            "message": "What is product-market fit?",
            "session_id": session_id,
            "mode": "chat",
        },
    )

    assert first_response.status_code == 200
    assert first_response.json()["session_id"] == session_id

    second_response = client.post(
        "/chat",
        json={
            "message": "What did we discuss earlier?",
            "session_id": session_id,
            "mode": "chat",
        },
    )

    assert second_response.status_code == 200
    assert second_response.json()["session_id"] == session_id
def test_essay_artifact_generation(monkeypatch):
    async def fake_run_growth_agent(question, history, mode):
        return {
            "answer": "# Test Essay\n\nThis is a test essay.",
            "sources": [
                {
                    "id": "source-1",
                    "title": "Test Source",
                    "content": "Test content",
                    "url": "https://example.com",
                }
            ],
        }

    monkeypatch.setattr(
        "backend.main.run_growth_agent",
        fake_run_growth_agent,
    )

    response = client.post(
        "/chat",
        json={
            "message": "Write an essay about product growth.",
            "mode": "essay",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["artifact"] is not None
    assert "<html" in data["artifact"].lower()
    assert "Test Essay" in data["artifact"]
def test_unsupported_question_is_handled_safely(monkeypatch):
    async def fake_run_growth_agent(question, history, mode):
        return {
            "answer": (
                "I don't have enough direct information in the "
                "provided sources."
            ),
            "sources": [],
        }

    monkeypatch.setattr(
        "backend.main.run_growth_agent",
        fake_run_growth_agent,
    )

    response = client.post(
        "/chat",
        json={
            "message": "What is the population of Mars?",
            "mode": "chat",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        "I don't have enough direct information"
        in data["answer"]
    )
    assert data["sources"] == []
def test_relevant_source_is_ranked_first():
    results = search_sources("product-market fit", limit=5)

    assert isinstance(results, list)

    if len(results) >= 2:
        assert (
            results[0]["relevance_score"]
            >= results[1]["relevance_score"]
        )
def test_chat_returns_source_traceability(monkeypatch):
    async def fake_run_growth_agent(question, history, mode):
        return {
            "answer": "This answer is based on the transcript.",
            "sources": [
                {
                    "id": "source-1",
                    "title": "Product Growth Interview",
                    "content": "Transcript content.",
                    "url": "https://example.com/source-1",
                    "relevance_score": 8,
                }
            ],
        }

    monkeypatch.setattr(
        "backend.main.run_growth_agent",
        fake_run_growth_agent,
    )

    response = client.post(
        "/chat",
        json={
            "message": "Explain product growth.",
            "mode": "chat",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["sources"]) == 1
    assert data["sources"][0]["id"] == "source-1"
    assert data["sources"][0]["title"] == "Product Growth Interview"
    assert data["sources"][0]["url"] == "https://example.com/source-1"