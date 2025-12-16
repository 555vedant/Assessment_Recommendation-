import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def extract_intent(query: str) -> dict:
    prompt = f"""
    You are extracting hiring intent.

    From the query below, extract:
    - hard_skills (list)
    - soft_skills (list)
    - role (string)
    - seniority (string or null)

    Return ONLY valid JSON.

    Query:
    {query}
    """

    model = genai.GenerativeModel("gemini-flash-latest")

    response = model.generate_content(prompt)

    return json.loads(response.text)
