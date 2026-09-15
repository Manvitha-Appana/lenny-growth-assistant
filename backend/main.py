import logging
import os
from backend.database import Base, engine, SessionLocal
from backend.models import Conversation, Message
import html
import re
from fastapi import FastAPI, HTTPException
from uuid import uuid4
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from backend.ollama_service import ask_llm
from backend.knowledge_base import search_sources
from backend.agent import run_growth_agent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)
app = FastAPI(title="Lenny Growth Assistant")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
conversation_history = {}
Base.metadata.create_all(bind=engine)

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    mode: str = "chat"

def markdown_to_html(text: str) -> str:
    text = html.escape(text)

    text = re.sub(
        r"\*\*(.*?)\*\*",
        r"<strong>\1</strong>",
        text
    )

    text = re.sub(
        r"^### (.*)$",
        r"<h3>\1</h3>",
        text,
        flags=re.MULTILINE
    )

    text = re.sub(
        r"^## (.*)$",
        r"<h2>\1</h2>",
        text,
        flags=re.MULTILINE
    )

    text = re.sub(
        r"^# (.*)$",
        r"<h1>\1</h1>",
        text,
        flags=re.MULTILINE
    )

    text = text.replace("\n", "<br>")

    return text
@app.get("/")
def home():
    return {"message": "Lenny Growth Assistant is running"}
@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "lenny-growth-assistant",
    }

@app.post("/knowledge-base/refresh")
def refresh_knowledge_base():
    try:
        from backend.ingest import ingest_transcript

        ingest_transcript()

        logger.info("Knowledge base refreshed successfully.")

        return {
            "status": "success",
            "message": "Knowledge base refreshed successfully.",
        }

    except Exception as error:
        logger.exception(
            "Knowledge base refresh failed: %s",
            error,
        )

        raise HTTPException(
            status_code=500,
            detail="Knowledge base refresh failed.",
        ) from error

@app.post("/chat")
async def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty.",
        )

    if request.mode not in ["chat", "essay"]:
        raise HTTPException(
            status_code=400,
            detail="Mode must be either 'chat' or 'essay'.",
        )
    session_id = request.session_id or str(uuid4())
    logger.info(
    "Chat request received: session_id=%s, mode=%s",
    session_id,
    request.mode,
    )
    db = SessionLocal()

    conversation = db.query(Conversation).filter_by(
    session_id=session_id
    ).first()

    if not conversation:
        conversation = Conversation(session_id=session_id)
        db.add(conversation)
        db.commit()
    history = conversation_history.get(session_id)

    if history is None:
        saved_messages = (
            db.query(Message)
            .filter_by(session_id=session_id)
            .order_by(Message.created_at)
            .all()
        )

        history = []

        for saved_message in saved_messages:
            history.append({
                "role": saved_message.role,
                "content": saved_message.content,
            })

        conversation_history[session_id] = history


    sources = search_sources(request.message)[:3]

    context = "\n\n".join(
        f"Source: {source.get('title', 'Unknown')}\n"
        f"{source.get('content', '')[:800]}"
        for source in sources
    )

    if request.mode == "essay":
        essay_instruction = """
Write a Ship 30 for 30-style essay of approximately 1,250 words.

Requirements:
- Start with a strong hook.
- Use a clear narrative progression.
- Add useful headings.
- Use short paragraphs, bullets, and bold emphasis where helpful.
- Give practical takeaways.
- Use only information supported by the provided transcript sources.
- Do not invent facts.
- If the sources are insufficient, clearly say so.
"""
    else:
        essay_instruction = """
Answer the user's question clearly and briefly.
"""

    prompt = f"""
You are The Lenny Growth Assistant.

{essay_instruction}

Rules:
1. Use information directly supported by the sources.
2. Give a clear and useful answer in simple language.
3. If the sources provide only partial information, explain what they do support.
4. Do not invent facts.
5. Mention the relevant speaker or topic when it appears in the transcript.
6. Use only sources that directly answer the user's question.
7. Do not combine unrelated transcript sections.
8. Do not make unsupported assumptions.
9. If a source is unrelated, ignore it.
10. Clearly state limitations.
11. Include source titles when presenting important information.
12. If the sources do not directly answer the question, say:
"I don't have enough direct information in the provided sources."

Sources:
{context}

Previous conversation:
{history}

User question:
{request.message}
"""

    try:
        agent_result = await run_growth_agent(
        question=request.message,
        history=history,
        mode=request.mode,
    )

        answer = agent_result["answer"]
        sources = agent_result["sources"]

    except Exception as error:
        logger.exception("Agent request failed: %s", re.error)
        raise HTTPException(
            status_code=503,
            detail="The growth assistant is currently unavailable.",
    )
    logger.info(
    "LLM response generated: provider=%s, session_id=%s",
    os.getenv("LLM_PROVIDER", "ollama"),
    session_id,
    )
    

    history.append({
    "role": "user",
    "content": request.message,
    })

    history.append({
    "role": "assistant",
    "content": answer,
    })
    conversation_history[session_id] = history[-20:]

    db.add(
        Message(
            session_id=session_id,
            role="user",
            content=request.message,
        )
    )

    db.add(
        Message(
            session_id=session_id,
            role="assistant",
            content=answer,
        )
    )

    db.commit()
    db.close()

    artifact = None

    if request.mode == "essay":
        artifact = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Lenny Growth Essay</title>
  <style>
    body {{
      font-family: Arial, sans-serif;
      max-width: 800px;
      margin: 40px auto;
      padding: 20px;
      line-height: 1.6;
    }}

    h1, h2, h3 {{
      color: #222;
    }}
  </style>
</head>
<body>
  <h1>Lenny Growth Essay</h1>
  <div>{markdown_to_html(answer)}</div>
</body>
</html>
"""

    return {
    "session_id": session_id,
    "answer": answer,
    "artifact": artifact,
    "sources": sources,
    "provider": os.getenv("LLM_PROVIDER", "ollama"),
}