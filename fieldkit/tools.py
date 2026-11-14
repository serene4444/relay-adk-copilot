from functools import lru_cache
from pathlib import Path

import chromadb
from chromadb.api.models.Collection import Collection
from google import genai
from google.genai import types
from google.adk.tools import ToolContext

CHROMA_DIR = Path(__file__).resolve().parent.parent / "data" / "chroma"
EMBED_MODEL = "gemini-embedding-001"


@lru_cache(maxsize=1)
def _get() -> tuple[genai.Client, Collection]:
    """Connect once, on first use, instead of at import time.

    lru_cache keeps the client alive, so it isn't garbage-collected (and closed)
    between tool calls.
    """
    client = genai.Client()
    collection = chromadb.PersistentClient(path=str(CHROMA_DIR)).get_collection("policies")
    return client, collection


def search_policies(query: str, tool_context: ToolContext) -> dict:
    """Search Linnet's policy documents (returns, shipping, quality promise).

    Args:
        query: What to look up, e.g. "can earrings be returned".

    Returns:
        The top matching policy sections with their document and section name.
    """
    client, col = _get()

    resp = client.models.embed_content(
        model=EMBED_MODEL,
        contents=query,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
    )
    if not resp.embeddings or not resp.embeddings[0].values:
        return {"error": "Embedding failed; try the search again."}
    query_vector: list[float] = resp.embeddings[0].values

    r = col.query(query_embeddings=[query_vector], n_results=3)
    metadatas = (r["metadatas"] or [[]])[0]
    documents = (r["documents"] or [[]])[0]

    results = [
        {"doc": str(m["doc"]), "section": str(m["section"]), "text": d}
        for m, d in zip(metadatas, documents)
    ]
    tool_context.state["policy_sources"] = results    # the reviewer reads this later
    return {"results": results}
