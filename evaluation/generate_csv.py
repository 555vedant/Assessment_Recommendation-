import pandas as pd
from recommender.recommend import recommend

df = pd.read_csv("data/Gen_AI_Dataset.csv")

print("CSV columns:", df.columns.tolist())

# Auto-detect query column
possible_cols = ["query", "Query", "input", "Input", "text", "jd", "JD"]

query_col = None
for col in possible_cols:
    if col in df.columns:
        query_col = col
        break

if query_col is None:
    raise ValueError(f"No query column found. Columns are: {df.columns.tolist()}")

queries = df[query_col].dropna().astype(str).unique()

rows = []

for q in queries:
    recs = recommend(q , useLLM=False)
    for r in recs:
        rows.append({
            "Query": q,
            "Assessment_url": r["assessment_url"]
        })

out = pd.DataFrame(rows)
out.to_csv("predictions.csv", index=False)

print("predictions.csv generated")
