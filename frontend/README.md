# MediBot Frontend

Expo web chat application for the MediBot backend RAG API.

## Backend dependency

Start the backend first from the repository root:

```bash
python main.py
```

The backend exposes:

- `GET /health`
- `POST /api/chat`
- `GET /docs`

## Setup

```bash
npm install
cp .env.example .env
npm run web
```

Set `EXPO_PUBLIC_API_BASE_URL` in `.env` for the backend URL:

- Local website: `http://localhost:8001`
- Deployed website: your deployed backend API origin

## Structure

```text
frontend/
├── App.js
├── src/
│   ├── api/          # Backend API calls
│   ├── components/   # Reusable UI components
│   ├── config/       # Environment configuration
│   └── screens/      # App screens
└── package.json
```
