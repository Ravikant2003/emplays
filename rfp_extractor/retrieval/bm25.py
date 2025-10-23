from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence, Tuple
import re

try:
    # Lightweight dependency. We also provide a graceful fallback below.
    from rank_bm25 import BM25Okapi  # type: ignore
except Exception:  # pragma: no cover - fallback path
    BM25Okapi = None  # type: ignore


_WORD_RE = re.compile(r"[A-Za-z0-9]+")


@dataclass(frozen=True)
class TextChunk:
    id: int
    text: str


def _tokenize(text: str) -> List[str]:
    return [t.lower() for t in _WORD_RE.findall(text)]


def chunk_text(
    text: str,
    chunk_chars: int = 1200,
    overlap_chars: int = 200,
) -> List[TextChunk]:
    if chunk_chars <= 0:
        raise ValueError("chunk_chars must be > 0")
    if overlap_chars < 0:
        raise ValueError("overlap_chars must be >= 0")

    normalized = text.replace("\r\n", "\n")
    chunks: List[TextChunk] = []
    start = 0
    idx = 0
    n = len(normalized)
    while start < n:
        end = min(start + chunk_chars, n)
        chunk = normalized[start:end]
        chunks.append(TextChunk(id=idx, text=chunk))
        idx += 1
        if end == n:
            break
        start = end - overlap_chars if overlap_chars > 0 else end
        if start < 0:
            start = 0
    return chunks


class _NaiveBM25:
    """Very small TF-idf-like scorer as a fallback when rank_bm25 is unavailable.
    This is intentionally simple and only used as a degradation path.
    """

    def __init__(self, tokenized_corpus: List[List[str]]):
        self.corpus = tokenized_corpus
        self.doc_freq = {}
        self.N = len(tokenized_corpus)
        for doc in tokenized_corpus:
            for term in set(doc):
                self.doc_freq[term] = self.doc_freq.get(term, 0) + 1

    def get_scores(self, query_tokens: Sequence[str]) -> List[float]:
        scores: List[float] = []
        for doc in self.corpus:
            score = 0.0
            if not doc:
                scores.append(score)
                continue
            term_counts = {}
            for t in doc:
                term_counts[t] = term_counts.get(t, 0) + 1
            for qt in query_tokens:
                df = self.doc_freq.get(qt, 0) or 1
                idf = max(0.0, (self.N / df))  # crude idf
                tf = term_counts.get(qt, 0) / len(doc)
                score += tf * idf
            scores.append(score)
        return scores


class BM25Retriever:
    def __init__(self, chunks: Sequence[TextChunk]):
        self.chunks: List[TextChunk] = list(chunks)
        self.tokenized_corpus: List[List[str]] = [_tokenize(c.text) for c in self.chunks]
        if BM25Okapi is not None:
            self.engine = BM25Okapi(self.tokenized_corpus)
        else:
            self.engine = _NaiveBM25(self.tokenized_corpus)

    def retrieve(self, query: str, top_k: int = 6) -> List[Tuple[TextChunk, float]]:
        if not self.chunks:
            return []
        query_tokens = _tokenize(query)
        scores = self.engine.get_scores(query_tokens)
        indexed = list(enumerate(scores))
        indexed.sort(key=lambda x: x[1], reverse=True)
        results: List[Tuple[TextChunk, float]] = []
        for idx, score in indexed[: max(1, top_k)]:
            results.append((self.chunks[idx], float(score)))
        return results


def build_rag_context(
    text: str,
    top_k: int = 8,
    query_hint: str | None = None,
) -> str:
    """Build a compact RAG context string by chunking and retrieving relevant passages.

    The query is formed from field names and synonyms if available, plus any user-provided hint.
    """
    from rfp_extractor.schema import FIELD_SYNONYMS

    chunks = chunk_text(text)
    retriever = BM25Retriever(chunks)

    field_terms: List[str] = []
    # Prioritize common field names as query terms
    field_terms.extend(
        [
            "bid",
            "number",
            "title",
            "due",
            "date",
            "submission",
            "type",
            "term",
            "pre",
            "meeting",
            "installation",
            "bond",
            "delivery",
            "payment",
            "documents",
            "mfg",
            "contract",
            "cooperative",
            "summary",
            "specification",
            "model",
            "part",
            "product",
            "contact",
            "company",
            "name",
        ]
    )
    # Include synonyms to improve recall
    for syns in FIELD_SYNONYMS.values():
        for s in syns:
            field_terms.extend(_tokenize(s))

    if query_hint:
        field_terms.extend(_tokenize(query_hint))

    query = " ".join(field_terms[:200])  # keep the query reasonable in size

    results = retriever.retrieve(query=query, top_k=top_k)
    if not results:
        return ""

    pieces: List[str] = []
    for rank, (chunk, score) in enumerate(results, start=1):
        # Keep chunk size bounded to avoid overlong prompts
        snippet = chunk.text.strip()
        if len(snippet) > 800:
            snippet = snippet[:800] + "\n..."
        pieces.append(f"[Passage {rank}]\n{snippet}")

    return "\n\n".join(pieces)
