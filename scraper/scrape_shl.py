import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

BASE_URL = "https://www.shl.com"
CATALOG_URL = "https://www.shl.com/solutions/products/product-catalog/"
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}



def scrape_table(table):
    assessments = []
    rows = table.find_all("tr")[1:]  # skip header

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 4:
            continue

        # Name + URL
        link = cols[0].find("a")
        if not link:
            continue

        name = link.text.strip()
        url = BASE_URL + link["href"]

        # Remote testing
        remote_support = "Yes" if cols[1].find("span", class_="-yes") else "No"

        # Adaptive / IRT
        adaptive_support = "Yes" if cols[2].find("span", class_="-yes") else "No"

        # Test type
        keys = cols[3].find_all("span", class_="product-catalogue__key")
        test_type = ", ".join(k.text.strip() for k in keys) if keys else "N/A"

        assessments.append({
            "name": name,
            "url": url,
            "test_type": test_type,
            "remote_support": remote_support,
            "adaptive_support": adaptive_support,
            "description": "N/A",
            "duration": "N/A"
        })

    return assessments


# -----------------------------
# Fetch description + duration
# -----------------------------
def enrich_from_detail(assessment):
    try:
        resp = requests.get(assessment["url"], headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")

        # Description
        desc_div = soup.find("div", class_="product-description")
        if desc_div:
            assessment["description"] = desc_div.get_text(" ", strip=True)

        # Duration (regex-based)
        text = soup.get_text(" ", strip=True).lower()
        match = re.search(r'(\d+)\s*(minute|min)', text)
        if match:
            assessment["duration"] = f"{match.group(1)} minutes"

    except Exception as e:
        print(f" Detail fetch failed: {assessment['url']}")

    return assessment


def scrape_shl_catalog():
    all_assessments = []

    print("🔍 Scraping Individual Test Solutions...")

    # type=1 → Individual Test Solutions
    for start in range(0, 400, 12):
        page_url = f"{CATALOG_URL}?start={start}&type=1"
        print("Fetching:", page_url)

        resp = requests.get(page_url, headers=HEADERS)
        if resp.status_code != 200:
            break

        soup = BeautifulSoup(resp.text, "html.parser")
        table = soup.find("table")
        if not table:
            break

        rows = scrape_table(table)
        if not rows:
            break

        all_assessments.extend(rows)
        time.sleep(1)

    print(f"Found {len(all_assessments)} assessments in catalog")

    # Enrich with detail pages
    for i, assessment in enumerate(all_assessments, 1):
        print(f"Enriching {i}/{len(all_assessments)}")
        enrich_from_detail(assessment)
        time.sleep(0.5)

    return pd.DataFrame(all_assessments)



if __name__ == "__main__":
    print(" Starting SHL catalog scraping...")
    df = scrape_shl_catalog()

    if len(df) < 377:
        print("ERROR: Less than 377 Individual Test Solutions found!")
    else:
        print("equirement satisfied")

    df.to_csv("data/shl_catalog.csv", index=False)
    print("Saved to data/shl_catalog.csv")
