"""Monolithic Streamlit frontend for Perplex AI.

The app keeps its own chat memory in ``st.session_state`` so follow-up questions
can inherit the recent conversation, and it renders both the model answer and
the research trail that produced it.
"""

from __future__ import annotations

import asyncio
import html
from datetime import datetime
from typing import Any, Dict, List

import streamlit as st

try:
    from backend.llm_orchestrate import (
        collect_synthesis_text,
        format_conversation_context,
        get_query_list,
    )
    from backend.web_search import web_search
except Exception as exc:  # pragma: no cover - surfaced in the UI at runtime
    st.set_page_config(page_title="Perplex AI", page_icon="🌆", layout="centered")
    st.error(
        "The research backend could not be imported. "
        "Check your environment variables and dependencies."
    )
    st.exception(exc)
    st.stop()


APP_TITLE = "Perplex AI"
DEFAULT_CONTEXT_TURNS = 4
DEFAULT_SEARCH_DEPTH = "advanced"
MAX_SOURCES_PER_QUERY = 5


def _set_page_shell() -> None:
    st.set_page_config(page_title=APP_TITLE, page_icon="🌆", layout="centered")
    st.markdown(
        """
        <style>
        .stApp {
            background:
            radial-gradient(circle at top left, rgba(255, 119, 89, 0.14), transparent 28%),
            radial-gradient(circle at top right, rgba(0, 60, 51, 0.10), transparent 26%),
            linear-gradient(180deg, #f8f4ee 0%, #f2eee7 45%, #f7f3ec 100%);
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(255,255,255,0.82), rgba(247,243,236,0.92));
            border-right: 1px solid rgba(23, 23, 28, 0.08);
        }
        .research-chrome {
            border: 1px solid rgba(23, 23, 28, 0.08);
            border-radius: 24px;
            padding: 1.1rem 1.25rem;
            background: rgba(255, 255, 255, 0.58);
            backdrop-filter: blur(10px);
            box-shadow: 0 20px 60px rgba(23, 23, 28, 0.06);
        }
        .research-kicker {
            text-transform: uppercase;
            letter-spacing: 0.22em;
            font-size: 0.72rem;
            color: rgba(23, 23, 28, 0.62);
            margin-bottom: 0.6rem;
        }
        .research-title {
            font-size: clamp(2.4rem, 4vw, 4.6rem);
            line-height: 0.95;
            letter-spacing: -0.05em;
            color: #17171c;
            margin: 0;
        }
        .research-subtitle {
            color: rgba(23, 23, 28, 0.66);
            max-width: 56rem;
            line-height: 1.6;
            margin-top: 0.8rem;
            font-size: 1rem;
        }
        .research-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            padding: 0.35rem 0.72rem;
            border: 1px solid rgba(23, 23, 28, 0.10);
            border-radius: 999px;
            background: rgba(255,255,255,0.55);
            font-size: 0.83rem;
            color: rgba(23, 23, 28, 0.72);
            margin: 0.15rem 0.25rem 0.15rem 0;
        }
        .stChatMessage {
            border-radius: 20px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _ensure_state() -> None:
    if "turns" not in st.session_state:
        st.session_state.turns = []
    if "context_turns" not in st.session_state:
        st.session_state.context_turns = DEFAULT_CONTEXT_TURNS
    if "search_depth" not in st.session_state:
        st.session_state.search_depth = DEFAULT_SEARCH_DEPTH


def _reset_chat() -> None:
    st.session_state.turns = []


def _trim_text(value: str, limit: int = 900) -> str:
    value = value.strip()
    if len(value) <= limit:
        return value
    return value[: limit - 1].rstrip() + "…"


def _render_raw_text_box(label: str, text: str) -> None:
    st.markdown(
        f"""
        <div style="margin: 0.35rem 0 0.8rem;">
        <div style="font-size: 0.72rem; letter-spacing: 0.18em; text-transform: uppercase; color: rgba(23,23,28,0.56); margin-bottom: 0.35rem;">
            {html.escape(label)}
        </div>
        <div style="
            white-space: pre-wrap;
            word-break: break-word;
            border: 1px solid rgba(23, 23, 28, 0.08);
            border-radius: 14px;
            padding: 0.85rem 0.95rem;
            background: rgba(255,255,255,0.72);
            color: rgba(23,23,28,0.84);
            line-height: 1.55;
            font-size: 0.92rem;
        ">{html.escape(text)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _build_context_block(turns: List[Dict[str, Any]], limit: int) -> str:
    recent_turns = turns[-limit:] if limit > 0 else []
    summarized_turns: List[Dict[str, str]] = []

    for turn in recent_turns:
        summarized_turns.append(
            {
                "query": _trim_text(turn.get("query", ""), 280),
                "answer": _trim_text(turn.get("answer", ""), 900),
            }
        )

    return format_conversation_context(summarized_turns, max_turns=limit)


def _extract_sources(web_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    sources: List[Dict[str, Any]] = []
    seen_urls = set()

    for search_index, result_batch in enumerate(web_results, start=1):
        search_query = result_batch.get("query", f"Search {search_index}")
        results = result_batch.get("results", []) or []

        for result_rank, result in enumerate(results[:MAX_SOURCES_PER_QUERY], start=1):
            url = result.get("url")
            if not url or url in seen_urls:
                continue

            seen_urls.add(url)
            sources.append(
                {
                    "index": len(sources) + 1,
                    "title": result.get("title") or url,
                    "url": url,
                    "query": search_query,
                    "search_index": search_index,
                    "result_rank": result_rank,
                    "snippet": result.get("content") or result.get("snippet") or "",
                    "score": result.get("score"),
                }
            )

    return sources


def _render_header() -> None:
    st.markdown(
        """
        <div class="research-chrome">
        <div class="research-kicker">Live research frontend</div>
        <h1 class="research-title">Search. Cite. Continue the conversation.</h1>
        <p class="research-subtitle">
            Ask a question, let the planner generate focused web searches, and keep
            the last few turns in context so follow-up questions do not start from zero.
        </p>
        <div style="margin-top: 0.9rem;">
            <span class="research-pill">Context-aware</span>
            <span class="research-pill">Search citations</span>
            <span class="research-pill">Source links</span>
            <span class="research-pill">Monolithic Streamlit UI</span>
        </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_turn(turn: Dict[str, Any]) -> None:
    with st.chat_message("user"):
        st.markdown(turn["query"])

    with st.chat_message("assistant"):
        st.markdown(turn["answer"])

        with st.expander("Research trail", expanded=False):
            st.markdown("**Search citations**")
            if turn["queries"]:
                for index, query in enumerate(turn["queries"], start=1):
                    st.markdown(
                        f"{index}. {html.escape(query)}", unsafe_allow_html=True
                    )
            else:
                st.caption("No planner queries were returned.")

            st.markdown("**Source citations**")
            if turn["sources"]:
                for source in turn["sources"]:
                    citation_label = f"[{source['index']}]"
                    st.markdown(
                        f"- {citation_label} [{html.escape(source['title'])}]({source['url']})",
                        unsafe_allow_html=True,
                    )
                    if source["snippet"]:
                        _render_raw_text_box(
                            f"From search {source['search_index']}",
                            source["snippet"],
                        )
            else:
                st.caption("No source URLs were returned by the web search step.")

            if turn.get("context_used"):
                st.markdown("**Context used**")
                st.code(turn["context_used"], language="text")


def _run_research(query: str) -> Dict[str, Any]:
    context_block = _build_context_block(
        st.session_state.turns, st.session_state.context_turns
    )

    progress = st.empty()
    progress.info("Planning search queries...")
    query_list = get_query_list(query, conversation_context=context_block)

    progress.info("Running live web searches...")
    web_results = web_search(query_list, search_depth=st.session_state.search_depth)

    progress.info("Synthesizing a cited answer...")
    answer = asyncio.run(
        collect_synthesis_text(
            query,
            web_results,
            conversation_context=context_block,
        )
    )
    progress.empty()

    return {
        "id": datetime.utcnow().isoformat(timespec="seconds"),
        "query": query,
        "answer": answer.strip() or "No answer was produced.",
        "queries": query_list,
        "web_results": web_results,
        "sources": _extract_sources(web_results),
        "context_used": context_block,
        "created_at": datetime.utcnow().isoformat(timespec="seconds"),
    }


_set_page_shell()
_ensure_state()

with st.sidebar:
    st.subheader("Research controls")
    st.caption("The conversation memory lives in this Streamlit session.")
    st.slider(
        "Turns included as context",
        min_value=0,
        max_value=8,
        value=st.session_state.context_turns,
        key="context_turns",
    )
    st.selectbox(
        "Search depth",
        options=["advanced", "basic"],
        index=0 if st.session_state.search_depth == "advanced" else 1,
        key="search_depth",
    )
    st.button("New chat", use_container_width=True, on_click=_reset_chat)
    st.divider()
    st.markdown(
        """
        <small>
        Search citations are shown separately from source citations so you can see
        both the planner's query trail and the URLs that grounded the answer.
        </small>
        """,
        unsafe_allow_html=True,
    )

_render_header()

for turn in st.session_state.turns:
    _render_turn(turn)

user_query = st.chat_input("Ask a follow-up or start a new research question...")

if user_query:
    with st.chat_message("user"):
        st.markdown(user_query)

    try:
        with st.chat_message("assistant"):
            turn = _run_research(user_query)
            st.markdown(turn["answer"])

            with st.expander("Research trail", expanded=False):
                st.markdown("**Search citations**")
                for index, query in enumerate(turn["queries"], start=1):
                    st.markdown(
                        f"{index}. {html.escape(query)}", unsafe_allow_html=True
                    )

                st.markdown("**Source citations**")
                if turn["sources"]:
                    for source in turn["sources"]:
                        st.markdown(
                            f"- [{source['index']}] [{html.escape(source['title'])}]({source['url']})",
                            unsafe_allow_html=True,
                        )
                        if source["snippet"]:
                            _render_raw_text_box(
                                f"From search {source['search_index']}",
                                source["snippet"],
                            )

                st.markdown("**Context used**")
                st.code(turn["context_used"], language="text")

        st.session_state.turns.append(turn)
    except Exception as exc:  # pragma: no cover - runtime safety net for the UI
        with st.chat_message("assistant"):
            st.error(f"Research failed: {exc}")
