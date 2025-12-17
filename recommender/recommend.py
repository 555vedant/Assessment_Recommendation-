import pandas as pd
import json
from recommender.retrieve import retrieve
from recommender.intent_llm import extract_intent
import google.generativeai as genai
import os

from dotenv import load_dotenv
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

df = pd.read_csv("data/shl_catalog.csv").fillna("")


def recommend(query, useLLM):
    intent = {}

    # llM #1 — Intent extraction
    if useLLM:
        try:
            intent = extract_intent(query)
        except Exception:
            intent = {}

    # build augmented query for vector search
    augmented_query = query
    if intent:
        augmented_query += " " + " ".join(intent.get("hard_skills", []))
        augmented_query += " " + " ".join(intent.get("soft_skills", []))

    # vector DB retrieval
    candidate_indices = retrieve(augmented_query, k=20)

    candidates = []
    for idx in candidate_indices:
        row = df.iloc[idx]
        candidates.append({
            "name": row["name"],
            "url": row["url"],
            "test_type": row["test_type"],
            "description": row["description"]
        })

# LLM 2 — Reranking
    selected_urls = [c["url"] for c in candidates[:5]]

    if useLLM:
        rerank_prompt = f"""
        You are selecting the most relevant SHL assessments.

        Hiring intent:
        {json.dumps(intent, indent=2)}

        Assessments:
        {json.dumps(candidates, indent=2)}

        Select the BEST 5 assessments.
        Return ONLY a JSON array of URLs in ranked order.
        """

        model = genai.GenerativeModel("gemini-flash-latest")
        response = model.generate_content(rerank_prompt)

        try:
            selected_urls = json.loads(response.text)
        except Exception:
            selected_urls = [c["url"] for c in candidates[:5]]

    # final response
    final_results = []
    for url in selected_urls:
        row = df[df["url"] == url].iloc[0]
        final_results.append({
            "assessment_name": row["name"],
            "assessment_url": row["url"],
            "description": row["description"],
            "test_type": row["test_type"],
            "duration": "Variable" if row["duration"] == "N/A" else row["duration"],
            "remote_support": row["remote_support"],
            "adaptive_support": row["adaptive_support"]
        })

    return final_results
