import subprocess
from groq_client import call_groq

def get_git_info():
    try:
        log = subprocess.check_output(
            ["git", "log", "--oneline", "--decorate", "--graph", "--all", "--stat", "--pretty=fuller"],
            stderr=subprocess.STDOUT
        ).decode(errors="ignore")
    except Exception as e:
        log = f"Could not get git log: {e}"

    try:
        status = subprocess.check_output(
            ["git", "status", "--short", "--branch"],
            stderr=subprocess.STDOUT
        ).decode(errors="ignore")
    except Exception as e:
        status = f"Could not get git status: {e}"

    return log, status

def git_summary():
    log, status = get_git_info()
    prompt = (
        "You are a senior software engineer and git expert. "
        "Given the following git log and status, provide a professional, technical, and human-readable summary. "
        "Summarize all commits, merges, and stages in a concise manner. "
        "Offer insights, highlight important changes, and suggest improvements or next steps if appropriate.\n\n"
        "=== GIT STATUS ===\n"
        f"{status}\n\n"
        "=== GIT LOG ===\n"
        f"{log}\n"
    )
    summary = call_groq(prompt, task_type="summarize")
    print("------ Git Summary ------")
    print(summary)
    print("-------------------------")