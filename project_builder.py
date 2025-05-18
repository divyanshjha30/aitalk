import sys
import os
import json
import subprocess
import re
from system_utils import make_dir, write_file, run_command
from groq_client import call_groq
import json5
import shutil
import time

def escape_multiline_strings(raw_json_str):
    """
    Escape newlines and quotes inside JSON string values of the "content" fields.
    This is needed because the LLM output uses raw newlines inside string values,
    which breaks strict JSON parsing.
    """
    pattern = r'("content"\s*:\s*")((?:[^"\\]|\\.|")*?)"(?=\s*[},])'

    def replacer(match):
        prefix = match.group(1)
        content = match.group(2)

        content_escaped = content.replace('\\', '\\\\')
        content_escaped = content_escaped.replace('"', '\\"')
        content_escaped = content_escaped.replace('\n', '\\n').replace('\r', '\\r')

        return f'{prefix}{content_escaped}"'

    fixed_str = re.sub(pattern, replacer, raw_json_str, flags=re.DOTALL)
    return fixed_str

def safe_run_command(cmd, cwd=None, max_retries=3):
    """
    Run a command with retries on failure.
    Returns True if succeeded, False otherwise.
    """
    env = os.environ.copy()
    env["CI"] = "true"  # Set CI environment to true to avoid prompts
    for attempt in range(1, max_retries + 1):
        try:
            print(f"🔄 Running command (attempt {attempt}): {' '.join(cmd)}")
            subprocess.run(cmd, cwd=cwd, env=env, check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Command failed on attempt {attempt}: {e}")
            if attempt < max_retries:
                print("⏳ Retrying after 5 seconds...")
                time.sleep(5)
            else:
                print("❌ Maximum retries reached. Giving up.")
                return False

def clean_node_modules(base_path):
    """
    Remove node_modules and lock files if they exist to prevent install conflicts.
    """
    node_modules_path = os.path.join(base_path, 'node_modules')
    if os.path.exists(node_modules_path):
        print("🧹 Removing existing node_modules folder...")
        shutil.rmtree(node_modules_path)

    for lockfile in ['package-lock.json', 'yarn.lock']:
        lockfile_path = os.path.join(base_path, lockfile)
        if os.path.exists(lockfile_path):
            print(f"🧹 Removing existing {lockfile} file...")
            os.remove(lockfile_path)

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

    cleaned = response.strip()
    cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", cleaned)
    cleaned = re.sub(r"```$", "", cleaned).strip()

    cleaned_fixed = escape_multiline_strings(cleaned)

    try:
        project = json5.loads(cleaned_fixed)
    except Exception as e:
        print("❌ Failed to parse JSON from LLM response.")
        print("Error:", e)
        print("=== Cleaned fixed JSON (partial) ===")
        print(cleaned_fixed[:500])
        sys.exit(1)

    print("✅ Parsed project structure:")
    print(json.dumps(project, indent=2))

    if not isinstance(project.get("files"), list) or not project['files']:
      print("❌ Invalid or empty 'files' list. Aborting.")
      sys.exit(1)

    base_path = os.path.join(os.getcwd(), project['project_name'])
    make_dir(base_path)
    for file in project['files']:
        file_path = os.path.join(base_path, file['path'])
        make_dir(os.path.dirname(file_path))
        print(f"📝 Writing to: {file_path}")

        content = file['content']

        # Special handling for package.json to remove double escaping
        if file['path'] == 'package.json':
            try:
                # Try normal JSON parse
                parsed_json = json.loads(content)
                content = json.dumps(parsed_json, indent=2)
            except Exception:
                try:
                    # If that fails, unescape and try again
                    unescaped = content.encode().decode('unicode_escape')
                    parsed_json = json.loads(unescaped)
                    content = json.dumps(parsed_json, indent=2)
                except Exception as e:
                    print("⚠️ Warning: Failed to parse package.json content for reformatting:", e)
                    # fallback: write raw content

        write_file(file_path, content)

    run_command(['git', 'init'], cwd=base_path)
    run_command(['git', 'add', '.'], cwd=base_path)
    run_command(['git', 'commit', '-m', 'Initial commit'], cwd=base_path)

    package_json_path = os.path.join(base_path, 'package.json')
    if os.path.exists(package_json_path):
        print("📦 Detected Node.js project, preparing for npm install...")

        # Clean old node_modules and lock files to avoid conflicts
        clean_node_modules(base_path)

        # Run npm install or npm ci depending on presence of package-lock.json
        lockfile_path = os.path.join(base_path, 'package-lock.json')
        if os.path.exists(lockfile_path):
            success = safe_run_command(['npm', 'ci'], cwd=base_path)
        else:
            success = safe_run_command(['npm', 'install'], cwd=base_path)

        if not success:
            print("❌ npm install failed after retries. Aborting.")
            sys.exit(1)

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
