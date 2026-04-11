# Coding Challenge Platform
A full-stack platform that generates coding challenges using OpenAI and tracks user progress.

## Features
- AI challenge generation across multiple difficulty levels
- Clerk authentication with JWT validation and user quota management
- Challenge history with filtering by difficulty and performance
- Multiple challenge types, including multiple-choice and short-answer

## Tech Stack
- **Frontend**: React, TypeScript, Vite, Clerk Auth
- **Backend**: FastAPI, Python, SQLAlchemy, SQLite
- **AI**: OpenAI API with server-side key management
- **Dev Tools**: Ngrok, uv

## Getting Started
**Prerequisites**
- Node.js and npm
- Python 3.8+
- Clerk account for authentication
- OpenAI API key

**Installation**
```bash
#Frontend setup
cd frontend
npm install
npm run dev

# Backend setup (in separate terminal)
cd backend
pip install -r requirements.txt
uv run server.py

# Webhook tunnel (in separate terminal)
ngrok http 8000

# Environment Variables
Create `.env.local` in frontend and backend directories with:
VITE_CLERK_PUBLISHABLE_KEY=your_key
CLERK_SECRET_KEY=your_secret
OPENAI_API_KEY=your_key
CLERK_WEBHOOK_SECRET=your_webhook_secret
```
