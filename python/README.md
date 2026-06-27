# Perplex AI — Python Edition

A search-powered AI assistant that mimics Perplexity's core functionality:
1. **User Query** → Web search via Tavily
2. **Search Results** → LLM synthesis via Gemini + LangChain
3. **Cited Answer** → With inline source citations
4. **Follow-ups** → 3 auto-generated questions, clickable or custom input

## Architecture

```
python/
├── backend/        FastAPI microservice (port 8000)
│   ├── models.py   Pydantic schemas
│   ├── search.py   Tavily web search
│   ├── llm.py      LangChain + Gemini chains
│   ├── main.py     FastAPI routes
│   ├── .env        API keys
│   └── requirements.txt
└── frontend/       Streamlit UI (port 8501)
    ├── app.py      Main chat interface
    └── requirements.txt
```

## Setup

### Prerequisites
- Python 3.10+
- API keys:
  - **TAVILY_API_KEY** (already in backend/.env)
  - **GOOGLE_API_KEY** (get from [Google AI Studio](https://aistudio.google.com/apikey))

### Backend Setup

```bash
cd python/backend
pip install -r requirements.txt
```

Update `.env` with your Google API key:
```
GOOGLE_API_KEY="your-key-here"
```

### Frontend Setup

```bash
cd python/frontend
pip install -r requirements.txt
```

## Running

### Terminal 1 — Backend
```bash
cd python/backend
uvicorn main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Terminal 2 — Frontend
```bash
cd python/frontend
streamlit run app.py
```

You should see:
```
You can now view your Streamlit app in your browser.
URL: http://localhost:8501
```

## Usage

1. Open http://localhost:8501 in your browser
2. Type a question (e.g., "What is LangChain?")
3. See the AI-generated answer with inline citations
4. Click a follow-up question OR type a new one
5. Full conversation history is preserved

## API Reference

### POST /search
Takes a query and conversation history, returns answer + sources + follow-ups.

**Request:**
```json
{
  "query": "What is machine learning?",
  "history": [
    {"role": "user", "content": "Previous question?"},
    {"role": "assistant", "content": "Previous answer..."}
  ]
}
```

**Response:**
```json
{
  "answer": "Machine learning is...[1][2]",
  "sources": [
    {
      "title": "Wikipedia - Machine Learning",
      "url": "https://...",
      "snippet": "Machine learning is a subset of AI..."
    }
  ],
  "follow_ups": [
    "What are the types of machine learning?",
    "How is it different from AI?",
    "What are practical applications?"
  ]
}
```

### GET /health
Health check endpoint.

**Response:**
```json
{"status": "ok"}
```

## Troubleshooting

**"Backend not running" error?**
- Ensure backend is started on port 8000
- Check: `curl http://localhost:8000/health`

**"GOOGLE_API_KEY not set"?**
- Get a free API key at [Google AI Studio](https://aistudio.google.com/apikey)
- Add it to `python/backend/.env`

**Slow responses?**
- First request is slower due to model loading
- Subsequent queries should be faster (model is cached)

## Features

- ✅ Web search via Tavily (advanced depth)
- ✅ LLM synthesis via Gemini 2.0 Flash
- ✅ Inline citation markers [1][2][3]
- ✅ Auto-generated follow-up questions
- ✅ Full conversation history tracking
- ✅ Manual query input override
- ✅ Expandable sources section
- ✅ Clean, responsive UI

## Next Steps

- [ ] Add streaming responses for faster feedback
- [ ] Persist conversation history to database
- [ ] Add export/share conversation feature
- [ ] Implement multi-turn RAG with memory
- [ ] Docker deployment setup
- [ ] User authentication
