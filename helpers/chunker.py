def chunk_text(text, chunk_size=1200, overlap=100):
    words = text.split()
    step = chunk_size - overlap
    return [
        " ".join(words[i:i + chunk_size])
        for i in range(0, len(words), step)
    ]