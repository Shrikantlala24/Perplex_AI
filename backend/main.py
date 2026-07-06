"""
main.py
FastAPI backend. Wires web_search.py + llm_orchestrate.py into one /query endpoint.

Flow per request:
1. Clerk JWT is verified — user_id extracted from the token's sub claim.
2. Plan search queries from the user's question   (non-streaming, fast)
3. Run Tavily search for each query                (non-streaming, sequential v1)
4. Stream the synthesized answer back over SSE      (this is the part users wait on)
"""

import logging

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from auth import verify_clerk_token
from web_search import web_search
from llm_orchestrate import get_query_list, stream_synthesis

logger = logging.getLogger(__name__)

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
async def query(
    request: QueryRequest,
    # verify_clerk_token runs before this handler.
    # It checks the Bearer token and returns the Clerk user_id (e.g. "user_2abc...").
    # If the token is missing or invalid, FastAPI returns 401/403 automatically.
    user_id: str = Depends(verify_clerk_token),
):
    # Log the authenticated user — plumbing for rate-limiting/history later.
    logger.info("[/query] user_id=%s query=%r", user_id, request.query[:80])

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
            # SSE format: "data: <text>\n\n"
            # Newlines inside a chunk are escaped so they don't break the event boundary.
            safe_chunk = chunk.replace("\n", "\\n")
            yield f"data: {safe_chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.get("/health")
async def health():
    # No auth — uptime checks and load balancer probes use this.
    return {"status": "ok"}
