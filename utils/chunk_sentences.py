from nltk.tokenize import sent_tokenize

def sentence_chunk_text(text, max_sentences=5):
    if not isinstance(text, str) or not text.strip():
        return []

    sentences = sent_tokenize(text)
    chunks = []

    for i in range(0, len(sentences), max_sentences):
        chunk = " ".join(sentences[i:i + max_sentences])
        if chunk.strip():
            chunks.append(chunk)

    return chunks