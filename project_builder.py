import sys
import os
import json
import subprocess
from system_utils import make_dir, write_file, run_command
from llm_utils import call_llm

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

    # Try to extract JSON robustly
    try:
        if '```' in response:
            response = response.split('```')[1]
        response = response.strip()
        start = response.find('{')
        end = response.rfind('}')
        json_data = response[start:end+1]
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
    run_command(['git', 'commit', '-m', 'First Commit'], cwd=base_path)

    # Technology-specific setup
    package_json_path = os.path.join(base_path, 'package.json')
    if os.path.exists(package_json_path):
        print("📦 Detected Node.js project, running npm install...")
        run_command(['npm', 'install'], cwd=base_path)

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