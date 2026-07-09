import os
from typing import List, Dict, AsyncIterator, Sequence

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser
from langchain_core.runnables import RunnableLambda
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load LLM API key
load_dotenv()

if not os.environ.get("GOOGLE_API_KEY"):
    raise RuntimeError("GOOGLE_API_KEY not set in environment")


# Model
model = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    temperature=0.5,
)


def _as_text(ai_message) -> str:
    """Normalize an AIMessage's content to a plain string.

    Gemini 3.x models can return `content` as a list of part-dicts
    (e.g. [{"type": "text", "text": "..."}]) instead of a plain string,
    which breaks StrOutputParser / PydanticOutputParser downstream.
    Older Gemini models (2.5 and earlier) always returned a str, so this
    is a compatibility shim for the 3.x response shape.
    """
    content = ai_message.content

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and item.get("type") == "text":
                parts.append(item.get("text", ""))
        return "".join(parts)

    return str(content)


_normalize_text = RunnableLambda(_as_text)


# Stage 1: query_list generation


# pydantic data model for query type validations
class SearchQueries(BaseModel):
    query_list: List[str] = Field(
        description=(
            "A list of concise search engine queries that together gather "
            "all information needed to answer the user's question."
        )
    )


# query parser
query_parser = PydanticOutputParser(pydantic_object=SearchQueries)


def format_conversation_context(
    history: Sequence[Dict[str, str]], max_turns: int = 4
) -> str:
    """Convert recent chat turns into a compact prompt context block."""

    if max_turns <= 0:
        return "No prior conversation."

    recent_turns = list(history)[-max_turns:]
    if not recent_turns:
        return "No prior conversation."

    lines = []
    for index, turn in enumerate(recent_turns, start=1):
        user_text = (turn.get("user") or turn.get("query") or "").strip()
        assistant_text = (turn.get("assistant") or turn.get("answer") or "").strip()

        if not user_text and not assistant_text:
            continue

        lines.append(f"Turn {index}:")
        if user_text:
            lines.append(f"User: {user_text}")
        if assistant_text:
            lines.append(f"Assistant: {assistant_text}")
        lines.append("")

    return "\n".join(lines).strip() or "No prior conversation."


# prompt template for getting query_list
query_prompt = PromptTemplate(
    template="""You are an expert search planner.

Your job is NOT to answer the user's question.
Instead, generate a list of search engine queries that will help collect the information needed.

Guidelines:
- Break complex questions into multiple focused searches.
- Each query should be short and specific.
- Avoid duplicate queries.
- Return between 3 and 8 queries depending on the complexity.
- Only return the structured output.

Relevant prior conversation:
{conversation_context}

User Question:
{user_query}

{format_instructions}
""",
    input_variables=["user_query", "conversation_context"],
    partial_variables={"format_instructions": query_parser.get_format_instructions()},
)


# chain for original_query -> model -> query_list
# _normalize_text sits between the model and the parser because Gemini 3.x
# can return content as a list of parts instead of a plain string.
query_chain = query_prompt | model | _normalize_text | query_parser


def get_query_list(user_query: str, conversation_context: str = "") -> List[str]:
    """Run the planning chain. Returns a validated list of search queries."""
    result = query_chain.invoke(
        {"user_query": user_query, "conversation_context": conversation_context}
    )
    return result.query_list


# Stage 2: final summarized response

# prompt
synthesis_prompt = ChatPromptTemplate.from_template(
    """You are an expert research analyst.

You have been provided with web search results from multiple search queries related to the user's question.

Your job is NOT to search again.
Your job is to synthesize, organize, compare, and explain the information from the provided search results.

USER QUESTION:
{user_query}

PRIOR CONVERSATION:
{conversation_context}

WEB SEARCH RESULTS:
{web_results}

Instructions:
1. Read every search result carefully.
2. Merge duplicate information from different sources into one coherent point.
3. Cite claims using the source URL in markdown, e.g. [Source](https://...).
4. Structure the answer with clear headings/sections where useful.
5. If the search results don't fully answer the question, say so explicitly instead of guessing.
"""
)


# final chain for prompt(including original_query, and query_responses) -> Model -> structured output
# NOTE: _normalize_text is inserted before StrOutputParser for the same
# Gemini 3.x list-content reason as above. This means .astream() below
# yields per-part chunks rather than exact per-token chunks -- still fine
# for SSE, just not byte-identical to raw token streaming.
synthesis_chain = synthesis_prompt | model | _normalize_text | StrOutputParser()


async def stream_synthesis(
    user_query: str,
    web_results: List[Dict],
    conversation_context: str = "",
) -> AsyncIterator[str]:
    """Async-stream the synthesis chain, chunk by chunk, for SSE."""
    async for chunk in synthesis_chain.astream(
        {
            "user_query": user_query,
            "web_results": web_results,
            "conversation_context": conversation_context,
        }
    ):
        yield chunk


async def collect_synthesis_text(
    user_query: str,
    web_results: List[Dict],
    conversation_context: str = "",
) -> str:
    """Collect the streamed synthesis into a single markdown string."""

    chunks = []
    async for chunk in stream_synthesis(
        user_query,
        web_results,
        conversation_context=conversation_context,
    ):
        chunks.append(chunk)
    return "".join(chunks)
