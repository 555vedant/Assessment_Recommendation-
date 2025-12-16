import os
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# def list_models():
#     models = genai.list_models()
#     for model in models:
#         print(f"Name: {model}")

# it worked finally thnx to stack overflow for fix lol

model = genai.GenerativeModel("gemini-flash-latest")

response = model.generate_content("Hello world!")
print(response.text)

# if __name__ == "__main__":
#     list_models()
