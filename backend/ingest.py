import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
TRANSCRIPT_FILE = BASE_DIR / "data" / "lenny_transcript.txt"
OUTPUT_FILE = BASE_DIR / "data" / "sources.json"


def ingest_transcript():
    text = TRANSCRIPT_FILE.read_text(encoding="utf-8").strip()

    chunk_size = 1500
    chunks = [
        text[i:i + chunk_size]
        for i in range(0, len(text), chunk_size)
    ]

    sources = []

    for index, chunk in enumerate(chunks, start=1):
        sources.append(
            {
                "id": f"lenny-transcript-{index}",
                "title": f"Lenny Podcast Transcript - Part {index}",
                "source_type": "transcript",
                "url": "https://www.lennyrachitsky.com/",
                "content": chunk,
            }
        )

    OUTPUT_FILE.write_text(
        json.dumps(sources, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"Created {len(sources)} source chunks.")


if __name__ == "__main__":
    ingest_transcript()