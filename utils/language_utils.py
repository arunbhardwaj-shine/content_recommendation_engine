from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
import pandas as pd
import pandas as pd

def is_english(text):
    if not isinstance(text, str) or not text.strip():
        return False
    try:
        return detect(text) == "en"
    except:
        return False

def detect_language(text):
    try:
        if pd.isna(text):
            return None
        text = str(text).strip()
        if not text:
            return None
        return detect(text)
    except LangDetectException:
        return None