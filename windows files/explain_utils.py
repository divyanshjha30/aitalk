import os
import getpass
import re
from groq_client import call_groq

def explain_last_n_commands_with_output(n, log_path=os.path.expanduser('~/aitalk_session.log')):
    if not os.path.exists(log_path):
        print(f"❌ Log file not found: {log_path}")
        print("Tip: Start your terminal session with: script ~/aitalk_session.log")
        return

    with open(log_path, 'r') as f:
        lines = f.readlines()

    def strip_ansi(line):
        ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
        return ansi_escape.sub('', line)

    # Find indices of prompts (lines ending with $ or % after stripping ANSI codes)
    prompt_indices = []
    for i, line in enumerate(lines):
        clean = strip_ansi(line).strip()
        if clean.endswith('$') or clean.endswith('%'):
            prompt_indices.append(i)

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
    explanation = call_groq(prompt, task_type="explain_x")
    print("------ LLM Explanation ------")
    print(explanation)
    print("-----------------------------")