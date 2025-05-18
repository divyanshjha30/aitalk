import os
import getpass
from llm_utils import call_llm

def explain_last_n_commands_with_output(n, log_path=os.path.expanduser('~/aitalk_session.log')):
    if not os.path.exists(log_path):
        print(f"❌ Log file not found: {log_path}")
        print("Tip: Start your terminal session with: script -f ~/aitalk_session.log")
        return

    with open(log_path, 'r') as f:
        lines = f.readlines()

    # Heuristic: Find lines that look like prompts (e.g., start with your username, $, or %)
    user = getpass.getuser()
    prompt_prefixes = [f"{user}@", "$", "%"]

    # Find indices of prompts
    prompt_indices = [i for i, line in enumerate(lines) if any(line.lstrip().startswith(p) for p in prompt_prefixes)]
    if not prompt_indices:
        print("❌ Could not find any command prompts in the log.")
        return

    # Get the last n command+output blocks
    blocks = []
    for i in range(len(prompt_indices)-1, max(-1, len(prompt_indices)-n-1), -1):
        start = prompt_indices[i]
        end = prompt_indices[i+1] if i+1 < len(prompt_indices) else len(lines)
        blocks.insert(0, "".join(lines[start:end]))

    session_snippet = "\n".join(blocks)

    prompt = f"""Explain step by step what is happening in these shell commands and their outputs:\n\n{session_snippet}"""
    explanation = call_llm(prompt)
    print("------ LLM Explanation ------")
    print(explanation)
    print("-----------------------------")