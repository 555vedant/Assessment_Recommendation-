# recommender/state.py
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer
import os

_df = None
_index = None
_model = None


def get_state():
    """
    Lazy-load everything only once.
    Render free-tier safe (prevents OOM).
    """
    global _df, _index, _model

    if _df is None:
        print("Loading SHL catalog CSV...")
        _df = pd.read_csv("data/shl_catalog.csv").fillna("")

    # Load embedding model
    if _model is None:
        print("Loading sentence-transformer model...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")

    # Load FAISS index (from recommender folder)
    if _index is None:
        print("Loading FAISS index...")
        faiss_path = os.path.join("recommender", "index.faiss")
        _index = faiss.read_index(faiss_path)

    return _df, _index, _model
