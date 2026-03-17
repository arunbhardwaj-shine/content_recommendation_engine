def clean_pdf_text(text: str) -> str:
    text = text.replace("-\n", "")
    text = text.replace("\n", " ")
    text = " ".join(text.split())
    return text

import re

def clean_text_for_biomed(text: str) -> str:
    if not isinstance(text, str):
        return ""

    text = text.replace("\x00", " ")        # null chars
    text = re.sub(r"\s+", " ", text)        # normalize whitespace
    text = text.strip()

    return text