import subprocess

def call_llm(prompt, model="codellama"):
    print(f"🤖 Calling Ollama locally with model: {model} ...")
    result = subprocess.run(
        ['ollama', 'run', model],
        input=prompt.encode(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    if result.stderr:
        print("⚠️ stderr:", result.stderr.decode())
    return result.stdout.decode()