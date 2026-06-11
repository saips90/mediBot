# Medibudi Frontend

Expo React Native chat app for the Medibudi backend RAG API.

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
npm start
```

Set `EXPO_PUBLIC_API_BASE_URL` in `.env` based on where the app runs:

- iOS simulator: `http://localhost:8001`
- Android emulator: `http://10.0.2.2:8001`
- Physical phone: `http://<your-computer-lan-ip>:8001`

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
