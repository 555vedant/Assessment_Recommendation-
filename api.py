from fastapi import FastAPI
from pydantic import BaseModel
from recommender.recommend import recommend

app = FastAPI()


class Query(BaseModel):
    query: str


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/recommend")
def recommend_api(q: Query):
    results = recommend(q.query, True)
    return {
        "query": q.query,
        "recommendations": results
    }
