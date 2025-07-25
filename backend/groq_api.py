import os
import requests
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def ask_groq(prompt, df_sample):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "messages": [
            {"role": "system", "content": "You are a data analyst who answers questions about CSV data."},
            {"role": "user", "content": f"Here is a sample of the data:\n\n{df_sample}"},
            {"role": "user", "content": prompt}
        ],
        "model": "llama3-70b-8192",
        "temperature": 0.3
    }

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=payload
    )

    response_json = response.json()
    message = response_json["choices"][0]["message"]["content"]
    tokens = response_json.get("usage", {}).get("total_tokens", 0)

    return message, None, tokens  # <-- now it returns 3 values
