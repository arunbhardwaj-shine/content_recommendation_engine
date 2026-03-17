import pandas as pd
import torch
from transformers import MarianMTModel, MarianTokenizer
from tqdm import tqdm
import re
MODEL_NAME = "Helsinki-NLP/opus-mt-ru-en"

class RUENTranslator:
    def __init__(self, device: str | None = None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        self.tokenizer = MarianTokenizer.from_pretrained(MODEL_NAME)
        self.model = MarianMTModel.from_pretrained(MODEL_NAME)

        self.model.to(self.device)
        self.model.eval()

    def translate_column(
        self,
        df: pd.DataFrame,
        source_col: str,
        target_col: str = "text_en",
        batch_size: int = 16,
        max_length: int = 512,
    ) -> pd.DataFrame:
        """
        Translate Russian text to English with progress monitoring.
        """

        texts = df[source_col].fillna("").astype(str).tolist()
        translations = []

        total_batches = (len(texts) + batch_size - 1) // batch_size

        for i in tqdm(
            range(0, len(texts), batch_size),
            total=total_batches,
            desc="Translating (RU → EN)",
            unit="batch",
        ):
            batch = texts[i:i + batch_size]

            inputs = self.tokenizer(
                batch,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=max_length,
            ).to(self.device)

            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=max_length,
                )

            decoded = self.tokenizer.batch_decode(
                outputs, skip_special_tokens=True
            )

            translations.extend(decoded)

        df[target_col] = translations
        return df


    def chunk_text(self, text: str, max_words: int = 400):
        words = text.split()
        return [
            " ".join(words[i:i + max_words])
            for i in range(0, len(words), max_words)
        ]

    def translate_text_any_length(self, text: str, max_length: int = 512) -> str:
        if not text or not text.strip():
            return ""

        if not re.search(r"[А-Яа-яЁё]", text):
            return text

        chunks = self.chunk_text(text)
        translated_chunks = []

        for chunk in chunks:
            inputs = self.tokenizer(
                chunk,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=max_length,
            ).to(self.device)

            with torch.no_grad():
                outputs = self.model.generate(**inputs, max_length=max_length)

            translated_chunks.append(
                self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            )
        print("DONE")
        return " ".join(translated_chunks)

    def translate_df_column(
        self,
        df: pd.DataFrame,
        source_col: str,
        target_col: str | None = None,
    ) -> pd.DataFrame:
        target_col = target_col or source_col
        df = df.copy()

        df[target_col] = df[source_col].astype(str).apply(
            self.translate_text_any_length
        )
        return df