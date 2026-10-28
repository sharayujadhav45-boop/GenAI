"""PDF parsing, chunking and lightweight keyword retrieval."""
from collections import Counter
import math
import os
import re
from pypdf import PdfReader

MAX_MB = 10


def extract_pdf_text(path: str) -> str:
    if os.path.getsize(path) > MAX_MB * 1024 * 1024:
        raise ValueError(f"PDF larger than {MAX_MB} MB.")
    text = "\n".join((p.extract_text() or "") for p in PdfReader(path).pages).strip()
    if not text:
        raise ValueError("No extractable text (scanned PDF?).")
    return text


def chunk(text: str, size: int = 400, overlap: int = 50):
    words = text.split()
    step = size - overlap
    return [" ".join(words[i:i + size]) for i in range(0, max(len(words), 1), step)]


def retrieve(text: str, query: str, k: int = 5) -> str:
    """Return the top-k chunks most relevant to the query (all text if short)."""
    chunks = chunk(text)
    if len(chunks) <= k:
        return "\n\n".join(chunks)

    terms = re.findall(r"\w+", (query or "key concepts definitions").casefold())
    query_terms = Counter(terms)
    tokenized = [re.findall(r"\w+", part.casefold()) for part in chunks]
    frequencies = [Counter(words) for words in tokenized]
    document_frequencies = Counter(
        term for counts in frequencies for term in counts.keys()
    )
    average_length = sum(map(len, tokenized)) / len(tokenized) or 1
    scored = []
    for index, counts in enumerate(frequencies):
        length = len(tokenized[index])
        score = 0.0
        for term, query_frequency in query_terms.items():
            frequency = counts.get(term, 0)
            if frequency:
                doc_frequency = document_frequencies[term]
                inverse_frequency = math.log(
                    1 + (len(chunks) - doc_frequency + 0.5) / (doc_frequency + 0.5)
                )
                normalized_frequency = (
                    frequency * 2.2
                    / (frequency + 1.2 * (0.25 + 0.75 * length / average_length))
                )
                score += query_frequency * inverse_frequency * normalized_frequency
        scored.append((score, index))

    best = sorted(scored, key=lambda result: (-result[0], result[1]))[:k]
    selected = sorted(index for _, index in best)
    return "\n\n".join(chunks[index] for index in selected)
