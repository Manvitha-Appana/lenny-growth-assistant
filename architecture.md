# System Architecture

## Overview

The Lenny Growth Assistant uses a frontend, FastAPI backend, transcript knowledge base, and Ollama language model.

## Architecture Flow

```text
User
  |
  v
Frontend
  |
  v
FastAPI Backend
  |
  +--> Knowledge Base Search
  |       |
  |       v
  |   Transcript Chunks
  |
  v
Prompt Construction
  |
  v
Ollama LLM
  |
  v
Generated Answer
  |
  v
Frontend Answer and Sources
Components
Frontend

The frontend is built using HTML, CSS, and JavaScript.

Responsibilities:

Accept user questions

Allow mode selection

Send requests to the backend

Display generated answers

Display source information

Display the session ID

FastAPI Backend

The backend exposes the /chat endpoint.

Responsibilities:

Validate incoming requests

Generate or reuse session IDs

Search transcript sources

Construct grounded prompts

Call the language model

Return answers and sources

Knowledge Base

The knowledge base contains transcript chunks stored in data/sources.json.

The ingestion script:

Reads the transcript text file.

Splits the text into chunks.

Adds metadata to each chunk.

Saves the result as JSON.

Ollama

Ollama runs the local llama3.2:3b model.

It generates answers based on the transcript context included in the prompt.

Request Flow

The user submits a question.

The frontend sends the question, session ID, and selected mode.

FastAPI searches the knowledge base.

The backend selects the top matching sources.

The backend constructs a grounding prompt.

Ollama generates the response.

FastAPI returns the answer, session ID, and sources.

The frontend displays the result.

Current Storage

The current prototype stores transcript data in JSON files.

The browser stores the session ID in sessionStorage.

Security Considerations

API keys should not be committed to the repository.

Generated content should be treated as untrusted.

Production deployment should use restricted CORS origins.

Generated HTML should be sanitized or rendered inside a sandboxed iframe.

Input length limits should be added for production use.

Future Architecture Improvements

PostgreSQL for conversation persistence

Vector database for semantic retrieval

Claude Agent SDK or Pi Coding Agent integration

Cloud model provider fallback

Docker Compose deployment

Structured logging

Automated monitoring

Automated tests

Dedicated Artifact Viewer