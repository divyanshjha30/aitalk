import os
from groq_client import call_groq

def summarise_file(prompt, file_path, model="mistral:7b"):
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    with open(file_path, 'r') as f:
        content = f.read()
    llm_prompt = f"Summarize this file based on the following instruction: '{prompt}'.\n\nFile content:\n{content}"
    summary = call_groq(llm_prompt, task_type="summarize")
    print("------ Summary ------")
    print(summary)
    print("---------------------")