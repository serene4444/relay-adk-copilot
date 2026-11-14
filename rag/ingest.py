"""Chunk the policy docs, embed them with Gemini, and store them in Chroma."""
import re
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from google import genai
from google.genai import types

ROOT = Path(__file__).resolve().parent.parent
POLICY_DIR = ROOT / "data" / "policies"
CHROMA_DIR = ROOT / "data" / "chroma"
EMBED_MODEL = "gemini-embedding-001"

load_dotenv(ROOT / "fieldkit" / ".env")


def chunk(path: Path):
    """One chunk per '## ' section, prefixed with the document title."""
    text = path.read_text(encoding="utf-8")
    title = text.splitlines()[0].lstrip("# ").strip()
    for section in re.split(r"\n(?=## )", text)[1:]:   # [0] is the title + intro
        heading = section.splitlines()[0].lstrip("# ").strip()
        yield {"doc": title, "section": heading, "text": f"{title}\n{section.strip()}"}


def main():
    chunks = [c for p in sorted(POLICY_DIR.glob("*.md")) for c in chunk(p)]

    client = genai.Client()
    result = client.models.embed_content(
        model=EMBED_MODEL,
        contents=[c["text"] for c in chunks],
        config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
    )

    vectors = [e.values or [] for e in (result.embeddings or [])]
    if len(vectors) != len(chunks) or not all(vectors):
        raise RuntimeError("Gemini returned missing embeddings; run ingest again.")

    db = chromadb.PersistentClient(path=str(CHROMA_DIR))
    try:
        db.delete_collection("policies")          # rebuild from scratch each run
    except Exception:
        pass
    col = db.create_collection("policies", configuration={"hnsw": {"space": "cosine"}})
    col.add(
        ids=[f"chunk-{i}" for i in range(len(chunks))],
        documents=[c["text"] for c in chunks],
        embeddings=vectors,  # pyright: ignore[reportArgumentType]  (Chroma's hints are stricter than its runtime)
        metadatas=[{"doc": c["doc"], "section": c["section"]} for c in chunks],
    )
    print(f"Indexed {len(chunks)} chunks into {CHROMA_DIR}")


if __name__ == "__main__":
    main()
