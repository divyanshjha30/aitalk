import sys
import os
import json
import subprocess
import re
from system_utils import make_dir, write_file, run_command
from groq_client import call_groq

def build_project(description, model="codellama"):
    prompt = f"""
You are a project code generator. Based on this prompt: "{description}", return ONLY a JSON with this structure:

{{
  "project_name": "todo-app",
  "files": [
    {{
      "path": "src/App.js",
      "content": "..."
    }},
    {{
      "path": "src/index.js",
      "content": "..."
    }},
    {{
      "path": "package.json",
      "content": "..."
    }},
    {{
      "path": "README.md",
      "content": "..."
    }}
  ]
}}

Requirements:
- The todo app must use localStorage to persist todos across refreshes.
- It must support adding, deleting, and toggling todos as complete/incomplete.
- It should include basic error handling (e.g., prevent empty input).
- It should include a README.md file describing how to run the project.
- Use React best practices (hooks, folder structure if possible).
- Do NOT include markdown formatting like triple backticks (```).
- Use modern JavaScript (ES6+).
- Use React 18 and the modern root API (createRoot).

Only return raw JSON in your output. No explanations.
"""

    response = call_groq(prompt, task_type="create_project")
    print("------ RAW RESPONSE ------")
    print(response)
    print("--------------------------")

    if not response:
        print("❌ No response from Groq API. Aborting.")
        sys.exit(1)

    # Remove triple backticks and any language hints
    cleaned = response.strip()
    cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", cleaned)
    cleaned = re.sub(r"```$", "", cleaned).strip()

    # Attempt to extract JSON
    try:
        start = cleaned.find('{')
        end = cleaned.rfind('}')
        json_data = cleaned[start:end+1]
        project = json.loads(json_data)
    except Exception as e:
        print("❌ Failed to parse JSON from LLM response.")
        print("Error:", e)
        sys.exit(1)

    print("✅ Parsed project structure:")
    print(json.dumps(project, indent=2))

    # Validate structure
    if not isinstance(project.get("files"), list) or not project['files']:
        print("❌ Invalid or empty 'files' list. Aborting.")
        sys.exit(1)

    # Create files
    base_path = os.path.join(os.getcwd(), project['project_name'])
    make_dir(base_path)
    for file in project['files']:
        file_path = os.path.join(base_path, file['path'])
        make_dir(os.path.dirname(file_path))
        print(f"📝 Writing to: {file_path}")
        write_file(file_path, file['content'])

    # Git Init and First Commit
    run_command(['git', 'init'], cwd=base_path)
    run_command(['git', 'add', '.'], cwd=base_path)
    run_command(['git', 'commit', '-m', 'Initial commit'], cwd=base_path)

    # Node setup
    package_json_path = os.path.join(base_path, 'package.json')
    if os.path.exists(package_json_path):
        print("📦 Detected Node.js project, running npm install...")
        run_command(['npm', 'install'], cwd=base_path)

    # Python setup if needed
    requirements_path = os.path.join(base_path, 'requirements.txt')
    if os.path.exists(requirements_path):
        print("🐍 Detected Python project, setting up virtual environment and installing requirements...")
        venv_path = os.path.join(base_path, 'venv')
        subprocess.run(['python3', '-m', 'venv', venv_path], cwd=base_path)
        pip_path = os.path.join(venv_path, 'bin', 'pip')
        subprocess.run([pip_path, 'install', '-r', 'requirements.txt'], cwd=base_path)

    print("🚀 Opening project in VS Code...")
    subprocess.Popen(['code', '-n', base_path])

    print(f"✅ Project '{project['project_name']}' created successfully!")