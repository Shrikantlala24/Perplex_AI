# Perplex AI

A Perplexity-style research assistant. You ask a question, it plans out a set of web searches, runs them, and writes a cited answer from what comes back. Built with Gemini (via LangChain), Tavily search, and a Streamlit frontend on top of a FastAPI backend.

## How it works

Two stages, both driven by Gemini:

1. **Query planning** — your question goes into a prompt that asks the model to break it into 3–8 focused search queries instead of answering directly. Output is validated against a Pydantic schema (`SearchQueries`) so you always get back a clean list of strings, not free text.
2. **Search and synthesize** — the query list is run through web search, and the results (plus the last few turns of conversation) get fed back into Gemini to write a single answer with markdown source links.

Conversation memory is just the last N turns of chat, summarized and trimmed, passed back into both stages as context. You control how many turns via a slider in the sidebar (0–8).

## Stack

- **LLM**: Gemini (`gemini-3.1-flash-lite`) through `langchain-google-genai`
- **Search**: Tavily
- **Backend**: FastAPI
- **Frontend**: Streamlit
- **Orchestration**: LangChain (prompt templates, output parsers, LCEL chains)

## Setup

```bash
pip install -r requirements.txt
```

Create a `.env` file with:

```
GOOGLE_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
```

Run the frontend:

```bash
streamlit run streamlit_app.py
```

## Project layout

```
backend/
  llm_orchestrate.py   # query planning + synthesis chains
  web_search.py         # Tavily wrapper
streamlit_app.py         # chat UI, session state, research trail display
```

## A quirk worth knowing about

`gemini-3.1-flash-lite` sometimes returns `message.content` as a list of parts instead of a plain string — older Gemini models don't do this. It'll silently break `StrOutputParser` and `PydanticOutputParser` if you don't handle it, so `llm_orchestrate.py` normalizes content to a string before either parser touches it. If you swap in a different Gemini model and start seeing empty or mangled output, this is the first thing to check.

## What's not here yet

- Searches inside a single turn run sequentially, not in parallel. Fine for now, slow for turns that need a lot of queries.
- The "research trail" (which queries were run, which sources were used) is shown per turn but isn't persisted anywhere — refresh the page and it's gone.
- No auth, no rate limiting, no persistence beyond the Streamlit session. This is a working prototype, not a deployed product.

## Notes on the two-stage design

Splitting planning from synthesis was a deliberate choice over a single-shot RAG call. It means you get to see and debug the actual search queries the model chose, and the synthesis step never has to guess what to search for, it just has to write from what's already in front of it. The tradeoff is two model calls instead of one, so latency is higher than a naive setup.
