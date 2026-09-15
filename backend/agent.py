
from backend.knowledge_base import search_sources
from backend.ollama_service import ask_llm


LIMITATION_MESSAGE = (
    "I don't have enough direct information in the provided sources."
)


async def run_growth_agent(
    question: str,
    history: list[dict],
    mode: str = "chat",
) -> dict:
    sources = search_sources(question, limit=3)

    context_parts = []

    for source in sources:
        source_id = source.get("id", "unknown")
        source_title = source.get("title", "Unknown")
        source_url = source.get("url", "Not available")
        source_content = source.get("content", "")[:1500]

        context_parts.append(
            f"Source ID: {source_id}\n"
            f"Source title: {source_title}\n"
            f"Source URL: {source_url}\n"
            f"Source content:\n{source_content}"
        )

    context = "\n\n".join(context_parts)

    if not context:
        context = "No relevant transcript sources were found."

    if mode == "essay":
        instruction = """
Write a Ship 30 for 30-style essay of approximately 1,250 words.

Requirements:
- Start with a strong hook.
- Use a clear narrative progression.
- Use useful headings.
- Use short paragraphs.
- Use bullets and bold emphasis where helpful.
- Include practical takeaways.
- Use only claims directly supported by the supplied transcript sources.
- Do not invent facts.
- Do not use outside knowledge.
- Do not make unsupported assumptions.
- End with a section titled "Sources Used".
- In "Sources Used", list only sources that directly support the essay.
- Include each source title and source ID.
"""
    else:
        instruction = """
Answer the user's question clearly and briefly using only the supplied sources.

Requirements:
- Use simple language.
- Answer only what the sources directly support.
- End with a section titled "Sources Used".
- In "Sources Used", list only sources that directly support the answer.
- Include each source title and source ID.
"""

    prompt = f"""
You are The Lenny Growth Assistant.

{instruction}

STRICT GROUNDING RULES:

1. The transcript sources are the only factual evidence you may use.
2. Do not use general knowledge, memory, assumptions, or outside information.
3. A keyword match does not prove that a source answers the question.
4. Do not infer, speculate, extrapolate, or create unsupported conclusions.
5. Do not combine unrelated source fragments to create a new claim.
6. If the sources do not directly answer the question, respond with exactly:
   "{LIMITATION_MESSAGE}"
7. If the sources answer only part of the question, provide only the supported
   part and clearly explain what is missing.
8. Never provide an unsupported answer after saying that the sources are insufficient.
9. Previous conversation is only for understanding context. It is not evidence.
10. Do not discuss unrelated topics.
11. Do not cite a source merely because it contains matching keywords.
12. Never invent source IDs, titles, URLs, speakers, or quotations.
13. If no source directly supports the answer, use the limitation message exactly.
14. The "Sources Used" section must not contain unsupported or unrelated sources.

Retrieved transcript sources:
{context}

Previous conversation:
{history}

User question:
{question}
"""

    answer = await ask_llm(prompt)

    if LIMITATION_MESSAGE in answer:
        answer = LIMITATION_MESSAGE

    return {
        "answer": answer,
        "sources": sources,
    }