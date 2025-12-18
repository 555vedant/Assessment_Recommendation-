from fastapi import FastAPI
from pydantic import BaseModel
from contextlib import asynccontextmanager

from recommender.recommend import recommend
from recommender.state import get_state
from recommender.debug_utils import log_event


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    log_event("STARTUP", "Preloading models and index...")
    get_state()
    log_event("STARTUP", "Preload complete")
    yield
    # Shutdown (optional)
    log_event("SHUTDOWN", "Application shutting down")


app = FastAPI(lifespan=lifespan)


class Query(BaseModel):
    query: str
    useLLM: bool = False


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/recommend")
def recommend_api(q: Query):
    results = recommend(q.query, q.useLLM)
    return {
        "query": q.query,
        "recommendations": results
    }
