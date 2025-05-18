import sys
import io
import os
import json
import subprocess
import re
from system_utils import make_dir, write_file, run_command
from groq_client import call_groq
import json5
import shutil
import time

# --- Meta-prompt generators ---

def generate_prompt_for_file_list(description):
    meta_prompt = f"""
You are a prompt engineer. Write a prompt for an LLM that will cause it to output ONLY a JSON array of all file paths (relative to the project root) needed for a modern, production-ready React 18 app, based on this user description: "{description}".

The LLM must output ONLY a JSON array (like ["package.json", "src/index.js", "public/index.html"]), with no explanations, no markdown, and no function calls or objects.

Return ONLY the prompt string to use. Do NOT include markdown or explanation.
"""
    prompt_string = call_groq(meta_prompt, task_type="generate_prompt")
    if not prompt_string:
        print("❌ Groq API did not return a prompt string. Check your API key, model, or network.")
        sys.exit(1)
    return prompt_string.strip().replace('“', '"').replace('”', '"')

def generate_prompt_for_file_content(description, filepath, previous_files):
    context_str = ""
    for fpath, content in previous_files.items():
        context_str += f"\nFile: {fpath}\n---\n{content}\n---\n"

    meta_prompt = f"""
You are a prompt engineer creating an ultra-precise prompt for an LLM that generates the full content of a single file in a modern React project.

Project Description:
\"\"\"{description}\"\"\"

Previously generated files with their content:
{context_str}

Now generate the full content of the file: "{filepath}"

RULES:
- Output only valid file content, no markdown or explanation.
- If it's JSON (like package.json), return valid JSON.
- Otherwise, output plain text/code.
- Output must work when written directly to a file.
- Do NOT add backticks, markdown, or any explanation.

Return ONLY the file content as plain text.
"""
    return meta_prompt

# 🔧 Improved file list parser
def extract_first_json_array(text):
    try:
        match = re.search(r'\[\s*"(?:[^"]|\\")*"\s*(?:,\s*"(?:[^"]|\\")*"\s*)*]', text, re.DOTALL)
        if not match:
            raise ValueError("No valid JSON array found in response.")
        array_str = match.group(0)
        return json5.loads(array_str)
    except Exception as e:
        raise ValueError(f"Could not extract JSON array: {e}")

def extract_first_json_object(text):
    """
    Attempts to find and return the first JSON object from a block of text.
    """
    brace_stack = []
    start_idx = None
    for i, ch in enumerate(text):
        if ch == '{':
            if start_idx is None:
                start_idx = i
            brace_stack.append(ch)
        elif ch == '}':
            if brace_stack:
                brace_stack.pop()
                if not brace_stack and start_idx is not None:
                    candidate = text[start_idx:i+1]
                    try:
                        parsed = json.loads(candidate)
                        return candidate
                    except:
                        start_idx = None
    return None

def get_project_name_from_description(description):
    name_prompt = f"""
You are an assistant that creates short, meaningful, hyphenated names for React apps based on a project description.

Return ONLY a short hyphenated name (lowercase, no spaces, no punctuation) for this project:
\"\"\"{description}\"\"\"
Example: "Admin dashboard with analytics and login" → "admin-dashboard"

Return ONLY the hyphenated name, no explanations, no markdown.
"""
    name = call_groq(name_prompt, task_type="generate_project_name")
    if not name:
        return "react-app"
    return re.sub(r"[^\w\-]", "", name.strip().lower())

def get_unique_project_dir(base_name):
    base_path = os.path.join(os.getcwd(), base_name)
    if not os.path.exists(base_path):
        return base_path

    i = 1
    while True:
        new_path = f"{base_path}-{i}"
        if not os.path.exists(new_path):
            return new_path
        i += 1

def get_file_list(description):
    effective_prompt = generate_prompt_for_file_list(description)
    response = call_groq(effective_prompt, task_type="create_project")
    if not response:
        print("❌ Groq API did not return a file list. Check your API key, model, or network.")
        sys.exit(1)

    print("------ RAW FILE LIST RESPONSE ------")
    print(response)
    print("--------------------------")

    try:
        file_list = extract_first_json_array(response)
        if not isinstance(file_list, list):
            raise ValueError("Parsed result is not a list.")
        return file_list
    except Exception as e:
        print("❌ Failed to parse file list from LLM response.")
        print("Error:", e)
        sys.exit(1)

def get_file_content_with_context(description, filepath, previous_files):
    prompt = generate_prompt_for_file_content(description, filepath, previous_files)
    response = call_groq(prompt, task_type="create_project")
    if not response:
        raise RuntimeError(f"Groq API did not return content for {filepath}.")
    cleaned = response.strip()
    cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", cleaned)
    cleaned = re.sub(r"```$", "", cleaned).strip()
    return cleaned

def build_project(description):
    file_list = get_file_list(description)
    project_name = get_project_name_from_description(description)
    base_path = get_unique_project_dir(project_name)
    print(f"📁 Creating project in: {base_path}")
    make_dir(base_path)

    # Save context of generated files
    files_content = {}
    failed_files = []

    print("🔄 Starting sequential generation with context passing...")
    i = 0
    while i < len(file_list):
        rel_path = file_list[i]
        print(f"📝 Generating content for: {rel_path} with context of {len(files_content)} files")

        retries = 0
        max_retries = 5
        while retries < max_retries:
            try:
                content = get_file_content_with_context(description, rel_path, files_content)
                files_content[rel_path] = content
                i += 1  # Only advance index if successful
                break  # Success, move to next file
            except Exception as e:
                error_message = str(e).lower()
                if "rate limit" in error_message or "429" in error_message:
                    wait_time = 5 * (retries + 1)
                    print(f"⚠️ Rate limit hit. Waiting {wait_time}s before retrying ({retries+1}/{max_retries})...")
                    time.sleep(wait_time)
                    retries += 1
                else:
                    print(f"❌ Failed to generate {rel_path}: {e}")
                    failed_files.append(rel_path)
                    i += 1  # Skip failed file and move on
                    break
        else:
            print(f"❌ Giving up on {rel_path} after {max_retries} retries.")
            failed_files.append(rel_path)
            i += 1

    # Write files to disk
    for rel_path, content in files_content.items():
        file_path = os.path.join(base_path, rel_path)
        make_dir(os.path.dirname(file_path))
        print(f"💾 Writing file: {file_path}")

        if rel_path == 'package.json':
            json_content = extract_first_json_object(content)
            if json_content:
                try:
                    parsed_json = json.loads(json_content)
                    # Add browserslist only if not already present
                    if "browserslist" not in parsed_json:
                        parsed_json["browserslist"] = {
                            "production": [
                                ">0.2%",
                                "not dead",
                                "not op_mini all"
                            ],
                            "development": [
                                "last 1 chrome version",
                                "last 1 firefox version",
                                "last 1 safari version"
                            ]
                        }
                    content = json.dumps(parsed_json, indent=2)
                except Exception as e:
                    print(f"⚠️ Warning: Could not parse extracted package.json content: {e}")
            else:
                print("⚠️ Warning: Could not extract a valid JSON object from package.json content.")

        write_file(file_path, content)

        # --- Inject react-scripts and start script if this is package.json ---
        if rel_path == 'package.json':
            package_path = file_path
            try:
                with open(package_path, 'r') as f:
                    pkg = json.load(f)
                scripts = pkg.setdefault('scripts', {})
                dependencies = pkg.setdefault('dependencies', {})
                if 'start' not in scripts:
                    scripts['start'] = 'react-scripts start'
                if 'react-scripts' not in dependencies:
                    dependencies['react-scripts'] = '5.0.1'
                with open(package_path, 'w') as f:
                    json.dump(pkg, f, indent=2)
            except Exception as e:
                print(f"⚠️ Could not patch react-scripts/start script in package.json: {e}")

    if failed_files:
        print("⚠️ The following files failed to generate:")
        for f in failed_files:
            print(f" - {f}")
    else:
        print("✅ All files generated successfully.")

    # ------------------------------
    # Now run git init, npm install, npm run start
    # ------------------------------

    # Run `git init`
    git_init_success = safe_run_command(["git", "init"], cwd=base_path)
    if git_init_success:
        # Make initial commit with message
        safe_run_command(["git", "add", "."], cwd=base_path)
        safe_run_command(["git", "commit", "-m", "Initial commit from our amazing kickass tool aitalk by Divyansh"], cwd=base_path)
    else:
        print("⚠️ git init failed, skipping git commit steps.")

    # Run npm install
    npm_success, npm_output = safe_run_command(["npm", "install"], cwd=base_path, capture_output=True)

    if not npm_success:
        print("❌ npm install failed. Attempting auto-repair via Groq...")

        package_path = os.path.join(base_path, "package.json")
        if not os.path.exists(package_path):
            print("❌ No package.json found to repair.")
            return

        with open(package_path, "r") as f:
            package_json_text = f.read()

        all_files = {}
        for root, dirs, files in os.walk(base_path):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, base_path)
                try:
                    with open(full_path, "r") as f:
                        all_files[rel_path] = f.read()
                except Exception:
                    continue

        repair_prompt = f"""
You are an expert in fixing npm errors in React projects.

The following `npm install` failed with this error:
{npm_output[:5000]}

Below is the current `package.json` file:
{package_json_text}

Please fix the `package.json` and return ONLY the fixed JSON (no explanation, no backticks, no markdown).

Make sure the new version fixes the issue and contains required dependencies for a modern React 18 app.
"""
        fixed_package = call_groq(repair_prompt, task_type="fix_package_json")
        cleaned_package = extract_first_json_object(fixed_package)
        if cleaned_package:
            try:
                parsed_fixed = json.loads(cleaned_package)

                # Inject browserslist again if needed
                if "browserslist" not in parsed_fixed:
                    parsed_fixed["browserslist"] = {
                        "production": [
                            ">0.2%",
                            "not dead",
                            "not op_mini all"
                        ],
                        "development": [
                            "last 1 chrome version",
                            "last 1 firefox version",
                            "last 1 safari version"
                        ]
                    }

                with open(package_path, "w") as f:
                    json.dump(parsed_fixed, f, indent=2)

                print("🔁 Replacing package.json and retrying npm install...")

                clean_node_modules(base_path)
                retry_success, _ = safe_run_command(["npm", "install"], cwd=base_path, capture_output=True)

                if retry_success:
                    print("✅ npm install fixed and completed!")
                    subprocess.Popen(["npm", "run", "start"], cwd=base_path)
                else:
                    print("❌ npm install failed even after repair.")
            except Exception as e:
                print("❌ Could not parse repaired package.json:", e)
        else:
            print("❌ Groq did not return a valid package.json.")
    else:
        print("✅ npm install succeeded. Starting project...")
        subprocess.Popen(["npm", "run", "start"], cwd=base_path)

# Utilities

def safe_run_command(cmd, cwd=None, max_retries=3, capture_output=False):
    env = os.environ.copy()
    env["CI"] = "true"
    for attempt in range(1, max_retries + 1):
        try:
            print(f"🔄 Running command (attempt {attempt}): {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                cwd=cwd,
                env=env,
                check=True,
                capture_output=capture_output,
                text=True
            )
            return True if not capture_output else (True, result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Command failed on attempt {attempt}: {e}")
            if capture_output and e.stderr:
                return False, e.stderr
            if attempt < max_retries:
                print("⏳ Retrying after 5 seconds...")
                time.sleep(5)
            else:
                print("❌ Maximum retries reached. Giving up.")
                return False if not capture_output else (False, e.stderr or "")

def clean_node_modules(base_path):
    node_modules_path = os.path.join(base_path, 'node_modules')
    if os.path.exists(node_modules_path):
        print("🧹 Removing existing node_modules folder...")
        shutil.rmtree(node_modules_path)
    for lockfile in ['package-lock.json', 'yarn.lock']:
        lockfile_path = os.path.join(base_path, lockfile)
        if os.path.exists(lockfile_path):
            print(f"🧹 Removing existing {lockfile} file...")
            os.remove(lockfile_path)