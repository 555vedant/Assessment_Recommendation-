# recommender/recommend.py
import json
import pandas as pd
import google.generativeai as genai
import os

from recommender.retrieve import retrieve
from recommender.intent_llm import extract_intent
from recommender.state import get_state

from dotenv import load_dotenv
load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def recommend(query, useLLM):
    # Lazy-load CSV
    df, _, _ = get_state()

    intent = {}

    # LLM #1 — Intent extraction
    if useLLM:
        try:
            intent = extract_intent(query)
            print("LLM1----------------------------------------------------------")
        except Exception:
            intent = {}

    # Query augmentation
    if useLLM and intent:
        augmented_query = query + " " + " ".join(
            intent.get("hard_skills", []) +
            intent.get("soft_skills", [])
        )
    else:
        augmented_query = query

    # Retrieval
    candidate_indices = retrieve(augmented_query, k=30)
    candidates_df = df.iloc[candidate_indices].copy()

    # Duration constraint
    if "minute" in query.lower():
        durations = (
            candidates_df["duration"]
            .str.extract(r"(\d+)")
            .astype(float)[0]
            .fillna(999)
        )
        candidates_df = candidates_df[durations <= 45]

    # Balance hard & soft skills
    hard = candidates_df[candidates_df["test_type"].str.contains("K", na=False)]
    soft = candidates_df[candidates_df["test_type"].str.contains("P|C", na=False)]

    final_df = pd.concat([hard.head(3), soft.head(2)]).head(5)

    # LLM #2 — Reranking
    if useLLM and not final_df.empty:
        print("LLM1----------------------------------------------------------")

        try:
            llm_candidates = final_df[
                ["name", "url", "description", "test_type"]
            ].to_dict("records")

            rerank_prompt = f"""
            You are selecting the most relevant SHL assessments.

            User query:
            {query}

            Assessments:
            {json.dumps(llm_candidates, indent=2)}

            Select the BEST 5 assessments.
            Return ONLY a JSON array of assessment URLs in ranked order.
            """

            model = genai.GenerativeModel("gemini-flash-latest")
            response = model.generate_content(rerank_prompt)

            selected_urls = json.loads(response.text)

            final_df = (
                final_df.set_index("url")
                .loc[[u for u in selected_urls if u in final_df["url"].values]]
                .reset_index()
            )

        except Exception:
            pass  # fallback to rule-based ranking

    # Final response
    final_results = []

    for _, row in final_df.iterrows():
        duration = row["duration"]
        if not duration or str(duration).strip().upper() == "N/A":
            duration = "Variable"

        final_results.append({
            "assessment_name": row["name"],
            "assessment_url": row["url"],
            "description": row["description"],
            "test_type": row["test_type"],
            "duration": duration,
            "remote_support": row["remote_support"],
            "adaptive_support": row["adaptive_support"]
        })

    return final_results
