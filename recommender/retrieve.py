# recommender/retrieve.py
import numpy as np
from recommender.state import get_state


def retrieve(query, k=50):
    """
    Vector search using FAISS.
    Model + index are lazy-loaded via state.
    """
    _, index, model = get_state()

    q_emb = model.encode([query]).astype("float32")
    _, indices = index.search(q_emb, k)

    return indices[0].tolist()
