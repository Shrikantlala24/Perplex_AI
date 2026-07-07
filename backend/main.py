from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from web_search import web_search
from llm_orchestrate import get_query_list, stream_synthesis

app = FastAPI(title="Perplex Clone API")

# Dev-only CORS — lock this to your actual frontend origin before shipping.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    query: str


@app.post("/query")
async def query(request: QueryRequest):
    user_query = request.query.strip()
    if not user_query:
        raise HTTPException(status_code=400, detail="query cannot be empty")

    # Stage 1: plan searches
    try:
        query_list = get_query_list(user_query)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"query planning failed: {e}")

    if not query_list:
        raise HTTPException(
            status_code=502, detail="planner returned no search queries"
        )

    # Stage 2: run search
    web_results = web_search(query_list)
    if not web_results:
        raise HTTPException(status_code=502, detail="all web searches failed")

    # Stage 3: stream synthesis as SSE
    async def event_stream():
        async for chunk in stream_synthesis(user_query, web_results):
            # SSE format: each event is "data: <text>\n\n"
            # Newlines inside chunk are escaped so they don't break the event boundary.
            safe_chunk = chunk.replace("\n", "\\n")
            yield f"data: {safe_chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.get("/health")
async def health():
    return {"status": "ok"}
