import pandas as pd

def extract_assessment_id(url):
    if not isinstance(url, str):
        return ""
    return url.split("product-catalog/view/")[-1].strip("/").lower()


def recall_at_k(true_urls, pred_urls, k=10):
    true_ids = set(extract_assessment_id(u) for u in true_urls)
    pred_ids = [extract_assessment_id(u) for u in pred_urls[:k]]

    if not true_ids:
        return 0.0

    hits = len(true_ids.intersection(pred_ids))
    return hits / len(true_ids)


true_df = pd.read_csv("data/Gen_AI_Dataset.csv")
pred_df = pd.read_csv("predictions.csv")

recalls = []

for q in true_df["Query"].unique():
    gt_urls = true_df[true_df["Query"] == q]["Assessment_url"].tolist()
    pred_urls = pred_df[pred_df["Query"] == q]["Assessment_url"].tolist()

    r = recall_at_k(gt_urls, pred_urls, k=10)
    recalls.append(r)

mean_recall = sum(recalls) / len(recalls) if recalls else 0.0

print("Mean Recall@10:", mean_recall)
