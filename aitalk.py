#!/usr/bin/env python3

import sys
import os
import subprocess
import json
import tempfile

# ---- System Call Helpers ----
def make_dir(path):
    os.makedirs(path, exist_ok=True)

def write_file(filepath, content):
    with open(filepath, 'w') as f:
        f.write(content)

def run_command(command, cwd=None):
    pid = os.fork()
    if pid == 0:
        os.execvp(command[0], command)
    else:
        os.wait()

# ---- Use Ollama to get response ----
def call_llm(prompt):
    print("🤖 Calling Ollama locally...")
    result = subprocess.run(
        ['ollama', 'run', 'codellama'],
        input=prompt.encode(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return result.stdout.decode()

# ---- Project Builder ----
def build_project(description):
    prompt = f"""
You are a project code generator. Based on this prompt: "{description}", 
return ONLY a JSON with this structure:

{{
  "project_name": "todo-app",
  "files": [
    {{
      "path": "src/App.js",
      "content": "import React from 'react'; ..."
    }},
    {{
      "path": "src/index.js",
      "content": "import ReactDOM from 'react-dom'; ..."
    }},
    {{
      "path": "package.json",
      "content": "{{\\n  \\"name\\": \\"todo-app\\", ... }}"
    }}
  ]
}}
"""

    response = call_llm(prompt)
    print("------ RAW RESPONSE ------")
    print(response)
    print("--------------------------")

    # Try to find JSON in response
    try:
        start = response.find('{')
        end = response.rfind('}')
        json_data = response[start:end+1]
        project = json.loads(json_data)
    except Exception as e:
        print("❌ Failed to parse JSON from LLM response.")
        print("Error:", e)
        sys.exit(1)

    # Create files
    base_path = os.path.join(os.getcwd(), project['project_name'])
    make_dir(base_path)
    for file in project['files']:
        file_path = os.path.join(base_path, file['path'])
        make_dir(os.path.dirname(file_path))
        write_file(file_path, file['content'])

    # Git Init
    run_command(['git', 'init', base_path])

    print(f"✅ Project '{project['project_name']}' created successfully!")

# ---- CLI Entry Point ----
if __name__ == "__main__":
    if '--create-project' in sys.argv:
        idx = sys.argv.index('--create-project')
        if len(sys.argv) > idx + 1:
            desc = sys.argv[idx + 1]
            build_project(desc)
        else:
            print("❌ Missing project description.")
    else:
        print("Usage:")
        print("  aitalk --create-project \"build a react todo app\"")

