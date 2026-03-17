def chunk_text(text, chunk_size=250, overlap=60):
    if not isinstance(text, str) or not text.strip():
        return []

    words = text.split()
    chunks = []
    i = 0

    while i < len(words):
        chunk = words[i:i + chunk_size]
        chunks.append(" ".join(chunk))
        i += chunk_size - overlap

    return chunks
