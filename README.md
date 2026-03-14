# 🧑‍💻 Coding Challenge Platform
A full-stack web application that generates dynamic coding challenges using AI and tracks user progress. Built with React, FastAPI, and OpenAI API integration, featuring secure authentication, real-time challenge generation, and comprehensive learning analytics.

## Features
- AI-powered coding challenge generation across multiple difficulty levels
- Secure user authentication with Clerk and JWT validation
- Real-time challenge history with filtering by difficulty and performance
- User quota management with 24-hour reset cycles
- Multiple challenge types, including multiple-choice and short-answer validation
- Progress tracking with detailed analytics and performance metrics
- Responsive design optimized for desktop and mobile

## Tech Stack
- **Frontend**: React, TypeScript, Vite, Clerk Auth, React Router
- **Backend**: FastAPI, Python, SQLAlchemy, SQLite
- **AI Integration**: OpenAI API with server-side key management
- **Authentication**: JWT tokens, Clerk webhooks
- **Dev Tools**: Ngrok (webhooks), uv (Python package manager)

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

## Usage
1. Sign up or log in via Clerk authentication
2. Select difficulty level (Easy, Medium, Hard)
3. Generate AI-powered coding challenges
4. Submit answers and receive instant feedback
5. View challenge history with filtering options
6. Track progress and performance metrics
