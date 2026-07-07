"""
web_search.py
Wraps Tavily search. One function in, list of raw result dicts out.
Sequential for v1 — parallelize with asyncio.gather in v2 once latency matters.
"""

import os
from typing import List, Dict
from tavily import TavilyClient

from dotenv import load_dotenv

load_dotenv()

TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")
if not TAVILY_API_KEY:
    raise RuntimeError("TAVILY_API_KEY not set in environment")

_client = TavilyClient(TAVILY_API_KEY)


def web_search(query_list: List[str], search_depth: str = "advanced") -> List[Dict]:
    """
    Run Tavily search for each query in query_list, sequentially.
    Returns a list of Tavily result dicts (one per query).
    Each dict has: query, results (list of {title, url, content, score, ...}), etc.

    Failures on individual queries are caught and skipped (not fatal) —
    a bad query shouldn't kill the whole research pipeline.
    """
    web_results = []

    for query in query_list:
        try:
            res = _client.search(query=query, search_depth=search_depth)
            web_results.append(res)
        except Exception as e:
            # Log and continue — partial results beat a hard failure.
            print(f"[web_search] query failed: {query!r} -> {e}")
            continue

    return web_results
