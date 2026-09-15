import os

import httpx
from anthropic import AsyncAnthropic
from dotenv import load_dotenv

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")

OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434",
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "llama3.2:3b",
)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.getenv(
    "ANTHROPIC_MODEL",
    "claude-3-5-haiku-latest",
)


async def ask_ollama(prompt: str) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }

    async with httpx.AsyncClient(timeout=300.0) as client:
        response = await client.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
        )

    response.raise_for_status()

    data = response.json()
    return data["response"]


async def ask_anthropic(prompt: str) -> str:
    if not ANTHROPIC_API_KEY:
        raise RuntimeError("ANTHROPIC_API_KEY is not configured.")

    client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)

    response = await client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=2000,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    return response.content[0].text


async def ask_llm(prompt: str) -> str:
    if LLM_PROVIDER == "anthropic":
        return await ask_anthropic(prompt)

    return await ask_ollama(prompt)