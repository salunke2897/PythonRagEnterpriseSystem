from collections.abc import Iterable

from utils.token_counter import count_tokens


def chunk_text(text: str, chunk_size: int, overlap: int, model: str) -> Iterable[str]:
    words = text.split()
    if not words:
        return []

    chunks: list[str] = []
    start = 0
    n_words = len(words)

    while start < n_words:
        end = min(start + chunk_size, n_words)
        chunk_words = words[start:end]

        while count_tokens(" ".join(chunk_words), model=model) > chunk_size and len(chunk_words) > 1:
            chunk_words = chunk_words[:-1]

        if not chunk_words:
            break

        chunks.append(" ".join(chunk_words))
        step = max(1, len(chunk_words) - overlap)
        start += step

    return chunks
