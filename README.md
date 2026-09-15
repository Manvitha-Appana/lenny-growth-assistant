
# The Lenny Growth Assistant

The Lenny Growth Assistant is a full-stack AI application that answers product and growth questions using transcript content from Lenny's Podcast and related growth material.

The application supports grounded conversational answers, source tracing, session-based conversation history, Ship 30 for 30-style essay generation, and an Artifact Viewer for generated essays.

## Features

- Product and growth question answering
- Transcript-based knowledge-base retrieval
- Relevance scoring for retrieved sources
- Source IDs, titles, and URLs returned with answers
- Session ID tracking
- Conversation persistence using SQLAlchemy and SQLite
- Provider configuration for Ollama and Anthropic
- Local LLM execution using Ollama
- Ship 30 for 30-style essay generation
- Generated HTML displayed in an isolated Artifact Viewer
- FastAPI backend
- Browser-based frontend
- Automated backend tests
- Structured application logging
- Knowledge-base ingestion and refresh

## Project Structure

```text
lenny-growth-assistant/
├── backend/
│   ├── __init__.py
│   ├── agent.py
│   ├── database.py
│   ├── ingest.py
│   ├── knowledge_base.py
│   ├── main.py
│   ├── models.py
│   └── ollama_service.py
├── data/
│   ├── lenny_transcript.txt
│   └── sources.json
├── frontend/
│   └── index.html
├── tests/
│   └── test_api.py
├── .env.example
├── .gitignore
├── architecture.md
├── design.md
├── DEVELOPMENT_LOG.md
├── docker-compose.yml
├── Dockerfile
├── PRD.md
├── README.md
└── requirements.txt
```

## Technologies Used

- Python
- FastAPI
- SQLAlchemy
- SQLite for local development
- PostgreSQL-compatible database configuration
- Ollama
- Llama 3.2 3B
- Anthropic SDK integration
- HTML
- CSS
- JavaScript
- JSON-based transcript knowledge base
- Pytest

## How It Works

1. The user enters a product or growth question.
2. The frontend sends the question to the FastAPI backend.
3. The backend creates or reuses a session.
4. The knowledge base searches the transcript chunks.
5. Relevant transcript chunks are ranked using keyword and title matching.
6. The selected source context is passed to the configured language model.
7. The model generates a grounded response.
8. The backend saves the conversation messages.
9. The frontend displays the answer and source information.
10. In essay mode, the generated content is also displayed in the Artifact Viewer.

## Running the Project

### 1. Activate the virtual environment

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. Configure environment variables

Create a `.env` file in the project root.

Example configuration:

```env
LLM_PROVIDER=ollama

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b

ANTHROPIC_API_KEY=
ANTHROPIC_MODEL=claude-3-5-haiku-latest

DATABASE_URL=sqlite+aiosqlite:///./lenny.db
```

Do not commit `.env` or any API keys to GitHub.

### 3. Start Ollama

Make sure Ollama is installed and running.

The configured local model is:

```text
llama3.2:3b
```

If the model is not installed, run:

```powershell
ollama pull llama3.2:3b
```

### 4. Start the backend

From the project root, run:

```powershell
python -m uvicorn backend.main:app --reload
```

The backend runs at:

```text
http://127.0.0.1:8000
```

Health check:

```text
http://127.0.0.1:8000/health
```

### 5. Start the frontend

Open another PowerShell terminal and run:

```powershell
python -m http.server 5500 --directory frontend
```

Open the frontend in a browser:

```text
http://127.0.0.1:5500
```

## Knowledge-Base Ingestion

The transcript is divided into smaller chunks and stored in:

```text
data/sources.json
```

To regenerate the knowledge base, run:

```powershell
python backend/ingest.py
```

The ingestion process:

- Reads `data/lenny_transcript.txt`
- Splits the transcript into chunks
- Adds source metadata
- Assigns source IDs
- Saves the chunks into `data/sources.json`

## Application Modes

### Normal Chat

Normal chat provides concise answers to product and growth questions using retrieved transcript context.

### Ship 30 for 30 Essay

Essay mode generates a structured essay with:

- A strong opening hook
- Narrative progression
- Clear headings
- Short paragraphs
- Bullets where useful
- Bold emphasis where useful
- Practical takeaways
- Transcript-grounded source context
- An HTML artifact displayed beside the conversation

## Grounding Approach

The assistant is instructed to:

- Use only the retrieved transcript context
- Avoid inventing unsupported facts
- Mention relevant source IDs and titles
- Explain limitations when the sources do not directly answer a question
- Distinguish incomplete source support from confirmed information
- Use conversation history for context without treating previous answers as source evidence

The retrieval system returns source metadata and relevance scores for traceability.

## LLM Provider Configuration

The application supports provider selection through the `LLM_PROVIDER` environment variable.

### Ollama

Ollama is the default local provider:

```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
```

Ollama allows the application to run locally without a cloud API key.

### Anthropic

Anthropic configuration is supported through the Anthropic SDK:

```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_api_key_here
ANTHROPIC_MODEL=claude-3-5-haiku-latest
```

The current demonstration uses Ollama because Claude/Anthropic authentication is not configured in the local development environment.

The Claude Agent SDK package is included in `requirements.txt`, but live Claude Agent SDK execution requires valid authentication.

## Database and Persistence

The application uses SQLAlchemy for database access.

The local development configuration uses SQLite:

```env
DATABASE_URL=sqlite+aiosqlite:///./lenny.db
```

Conversation records and messages are stored with session IDs and timestamps.

The database configuration is designed to support PostgreSQL-compatible URLs for deployment, although a live PostgreSQL service is not configured in the local demonstration.

## Artifact Viewer and Safety

Essay mode generates an HTML artifact.

The frontend displays the artifact in a sandboxed iframe:

```html
<iframe sandbox="allow-scripts">
```

Generated HTML is treated as untrusted content. The sandbox limits the artifact's access to the surrounding application.

## Testing

Run the automated API test suite with:

```powershell
python -m pytest -q tests/test_api.py
```

The test suite covers:

- Health endpoint behavior
- Empty-message validation
- Invalid mode validation
- LLM failure handling
- Provider information
- Knowledge-base retrieval
- Relevance ranking
- Conversation persistence
- Essay artifact generation
- Unsupported-question handling
- Source traceability

## Manual UI Test Plan

1. Open the frontend in the browser.
2. Ask a normal product-growth question.
3. Verify that an answer is displayed.
4. Verify that source information is displayed.
5. Select Essay mode.
6. Generate an essay.
7. Verify that the Artifact Viewer displays the essay.
8. Ask a follow-up question in the same session.
9. Verify that the session ID remains unchanged.
10. Refresh the page.
11. Verify that the application loads correctly.
12. Submit an empty question.
13. Verify that the frontend shows a validation message.
14. Stop Ollama and verify that the application displays an error response gracefully.

## Docker

Docker support is included through `Dockerfile` and `docker-compose.yml`.

If Docker is installed, run:

```powershell
docker compose up --build
```

Docker Compose has not been tested in the current Windows development environment because Docker is not installed locally.

## Documentation

Additional project documentation is available in:

- `PRD.md` — product requirements
- `design.md` — interface and user-experience design
- `architecture.md` — technical architecture
- `DEVELOPMENT_LOG.md` — development progress, decisions, testing, and limitations

## Current Limitations

- The default local model is Ollama with `llama3.2:3b`.
- Anthropic support is configurable, but it requires a valid API key.
- Claude Agent SDK execution could not be fully verified because authentication was unavailable during development.
- Retrieval currently uses keyword-based matching rather than vector embeddings.
- SQLite is used by default for local development.
- PostgreSQL configuration is supported through `DATABASE_URL`, but a live PostgreSQL deployment has not been verified.
- Docker configuration is included but has not been tested on this machine.
- The application is intended as a local demonstration and has not yet been deployed to production.