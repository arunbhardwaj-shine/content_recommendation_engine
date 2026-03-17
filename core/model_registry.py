from core.markov_model import MarkovRecommender
from helpers.data_loader import load_user_sequences
from utils.db_utils import get_engine
engine = get_engine()

import threading
import time

markov_model = MarkovRecommender()


def initialize_models():
    df = load_user_sequences(engine)
    markov_model.train(df)


def auto_refresh(interval_seconds=3600):
    while True:
        time.sleep(interval_seconds)
        print("🔄 Refreshing Markov model...")
        df = load_user_sequences(engine)
        markov_model.train(df)
        print("✅ Markov model refreshed.")


def start_background_refresh():
    thread = threading.Thread(
        target=auto_refresh,
        daemon=True
    )
    thread.start()