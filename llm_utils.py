import subprocess

def call_llm(prompt):
    print("🤖 Calling Ollama locally...")
    result = subprocess.run(
        ['ollama', 'run', 'codellama'],
        input=prompt.encode(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    if result.stderr:
        print("⚠️ stderr:", result.stderr.decode())
    return result.stdout.decode()