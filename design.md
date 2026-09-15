# Design Document

## Design Goals

The interface should be simple, readable, and focused on asking product and growth questions.

## Main Screen

The main screen contains:

1. Application title
2. Session ID indicator
3. Mode selector
4. Question input box
5. Ask button
6. Answer area
7. Source area

## User Flow

1. The user opens the application.
2. The user selects either Normal Answer or Ship 30 for 30 Essay.
3. The user enters a question.
4. The frontend sends the question to the backend.
5. The backend retrieves relevant transcript chunks.
6. Ollama generates a response.
7. The answer and sources are displayed.

## Interaction Design

- Empty questions show a validation message.
- The answer area displays a loading message while processing.
- The session ID is visible to the user.
- Sources are displayed below the answer.
- The mode selector allows users to switch between short answers and essays.

## Visual Design

- Clean white background
- Simple typography
- Clear spacing
- Readable answer area
- Minimal controls
- Source information separated from the answer

## Error Handling

The interface displays an error message when:

- The backend is unavailable
- Ollama is unavailable
- The request fails
- The response cannot be generated

## Future Design Improvements

- Two-column chat and Artifact Viewer layout
- Conversation history panel
- Better source cards
- Loading spinner
- Mobile-responsive layout
- Markdown rendering
- Accessible keyboard navigation