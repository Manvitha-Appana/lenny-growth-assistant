import json
import re
from pathlib import Path


DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "sources.json"


def load_sources() -> list[dict]:
    if not DATA_FILE.exists():
        return []

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def tokenize(text: str) -> set[str]:
    return set(
        re.findall(
            r"\b[a-zA-Z0-9]+\b",
            text.lower(),
        )
    )


def search_sources(
    query: str,
    limit: int = 5,
) -> list[dict]:
    sources = load_sources()

    if not query.strip():
        return []

    query_terms = tokenize(query)

    if not query_terms:
        return []

    scored_sources = []

    for source in sources:
        title = source.get("title", "")
        content = source.get("content", "")
        source_text = f"{title} {content}"

        source_terms = tokenize(source_text)

        matching_terms = query_terms.intersection(source_terms)

        if not matching_terms:
            continue

        score = len(matching_terms)

        title_terms = tokenize(title)
        title_matches = query_terms.intersection(title_terms)

        score += len(title_matches) * 3

        content_lower = content.lower()
        query_lower = query.lower()

        if query_lower in content_lower:
            score += 5

        scored_sources.append(
            {
                "score": score,
                "source": source,
            }
        )

    scored_sources.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    results = []

    for item in scored_sources[:limit]:
        source = dict(item["source"])
        source["relevance_score"] = item["score"]
        results.append(source)

    return results