import os
from llm_utils import call_llm

def summarise_file(prompt, file_path, model="mistral:7b"):
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    with open(file_path, 'r') as f:
        content = f.read()
    llm_prompt = f"Summarize this file based on the following instruction: '{prompt}'.\n\nFile content:\n{content}"
    summary = call_llm(llm_prompt, model=model)
    print("------ Summary ------")
    print(summary)
    print("---------------------")