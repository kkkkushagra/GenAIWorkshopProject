# College Knowledge Assistant

A FastAPI-based service for answering college-related questions using institutional policy documents.

## Features
- Academic, attendance, placement, and hostel query support
- Source citations in every answer
- JSON API for easy integration
- Production-ready deployment setup for Render

## Folder Structure
- assistant.py: existing backend logic
- app.py: FastAPI application wrapper
- data/: institutional policy documents
- render.yaml: Render deployment configuration

## Installation
```bash
pip install -r requirements.txt
```

## Run Locally
```bash
uvicorn app:app --reload
```

## API Endpoints
- GET /
- GET /health
- POST /chat

## Example Request
```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the attendance requirement?"}'
```

## Example Response
```json
{
  "answer": "Based on the retrieved policy, students must maintain at least 75% attendance to appear in examinations.",
  "source": "Attendance Policy"
}
```

## Deploy on Render
1. Push this project to GitHub.
2. Sign in to Render.
3. Create a new Web Service.
4. Connect your GitHub repository.
5. Use the build command:
   ```bash
   pip install -r requirements.txt
   ```
6. Use the start command:
   ```bash
   uvicorn app:app --host 0.0.0.0 --port $PORT
   ```
7. Deploy the service.

Render will provide a public URL for your deployed app.
