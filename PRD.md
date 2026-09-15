# Product Requirements Document

## Product Name

The Lenny Growth Assistant

## Problem

Product managers and growth teams often need practical advice about product strategy, growth, user research, and product-market fit.

The assistant makes Lenny's Podcast transcript knowledge easier to search and apply.

## Target Users

- Product managers
- Growth professionals
- Startup founders
- Product designers
- Students learning product management

## Goals

1. Answer product and growth questions using transcript content.
2. Show the sources used for each answer.
3. Avoid unsupported claims.
4. Support normal answers and long-form essays.
5. Maintain a session identifier for each user session.
6. Provide a simple and easy-to-use interface.

## Core Features

### Conversational Questions

Users can ask product and growth questions through a chat interface.

### Transcript Retrieval

The system searches transcript chunks and selects relevant content.

### Grounded Answers

The assistant uses retrieved transcript content and explains when information is insufficient.

### Source Display

The frontend displays the source titles used to generate the answer.

### Essay Mode

Users can request a Ship 30 for 30-style essay with:

- A strong opening hook
- Clear headings
- Narrative progression
- Practical takeaways
- Transcript-grounded claims

### Session Tracking

Each conversation receives a session ID that is displayed in the interface.

## Non-Functional Requirements

- FastAPI backend
- Local Ollama model support
- Clear error messages
- No secrets committed to the repository
- Simple local setup
- Responsive browser interface

## Success Criteria

The prototype is successful when:

1. A user can ask a question.
2. The backend retrieves transcript context.
3. Ollama generates an answer.
4. The frontend displays the answer.
5. Sources are visible.
6. Essay mode produces structured content.
7. Empty questions are handled safely.

## Future Improvements

- PostgreSQL conversation persistence
- Cloud LLM provider support
- Claude Agent SDK or Pi Coding Agent integration
- Semantic vector retrieval
- Artifact Viewer
- Automated tests
- Docker Compose deployment