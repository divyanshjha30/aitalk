import requests
import os
from dotenv import load_dotenv
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

TASK_MODEL_MAP = {
    "create_project": "meta-llama/llama-4-scout-17b-16e-instruct",
    "summarize": "meta-llama/llama-4-scout-17b-16e-instruct",
    "explain_x": "meta-llama/llama-4-scout-17b-16e-instruct"
}

def call_groq(prompt, task_type="create_project", system_prompt="You are a helpful assistant.", model=None):
    if model is None:
        model = TASK_MODEL_MAP.get(task_type, "meta-llama/llama-4-scout-17b-16e-instruct")
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }
    try:
        resp = requests.post(url, headers=headers, json=data)
        resp.raise_for_status()
        result = resp.json()
        return result["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        print(f"Groq API Error: {e}")
        try:
            print("Groq API response:", resp.text)
        except Exception:
            pass
        return None