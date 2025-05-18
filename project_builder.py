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

def generate_prompt_for_all_files_content(description, file_list, files_content_so_far):
    """
    Generates a prompt for the LLM to produce content for all files at once,
    passing previously generated files as context.
    files_content_so_far: dict of {filepath: content}
    """
    # Format already generated files for context
    context_str = ""
    for fpath, content in files_content_so_far.items():
        context_str += f"\nFile: {fpath}\n---\n{content}\n---\n"

    meta_prompt = f"""
You are a highly capable LLM that generates a modern, production-ready React 18 app.

Project Description:
\"\"\"{description}\"\"\"

You have already generated the following files with their full content:
{context_str}

Now, generate the full content of the remaining files exactly as specified in this file list:
{json.dumps(file_list)}

Output ONLY a JSON object where keys are file paths and values are their full file content as strings.

Rules:
- Do NOT include markdown or code fences.
- Output valid JSON only.
- Each file content must be complete and exactly what should be written to the file.
- Make sure the files are consistent and reference each other properly.

Return ONLY the JSON object as text.
"""
    return meta_prompt

def generate_prompt_for_file_content(description, filepath, previous_files):
    # If you want to generate one file at a time with context of previous files:
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


def get_all_files_content(description, file_list):
    """
    Generate all files in one shot, passing the entire file list and any previously generated content.
    Falls back to single file generation if needed.
    """
    # First, try one-shot generation for all files
    prompt = generate_prompt_for_all_files_content(description, file_list, {})
    response = call_groq(prompt, task_type="create_project")
    if not response:
        print("❌ Groq API did not return project files content. Trying sequential generation...")
        return None

    try:
        files_content = json.loads(response)
        if not isinstance(files_content, dict):
            raise ValueError("Response is not a JSON object.")
        # Check if all files are present
        if not all(f in files_content for f in file_list):
            raise ValueError("Not all files are present in response.")
        return files_content
    except Exception as e:
        print(f"⚠️ Could not parse one-shot file content JSON or incomplete: {e}")
        return None

def get_file_content_with_context(description, filepath, previous_files):
    prompt = generate_prompt_for_file_content(description, filepath, previous_files)
    response = call_groq(prompt, task_type="create_project")
    if not response:
        print(f"❌ Groq API did not return content for {filepath}. Check your API key, model, or network.")
        sys.exit(1)
    cleaned = response.strip()
    cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", cleaned)
    cleaned = re.sub(r"```$", "", cleaned).strip()
    return cleaned

def build_project(description):
    file_list = get_file_list(description)
    project_name = os.path.basename(os.path.splitext(file_list[0])[0]) if file_list and file_list[0].endswith("package.json") else "react-app"
    base_path = os.path.join(os.getcwd(), project_name)
    make_dir(base_path)

    # Try one-shot generation of all files
    print("🧩 Attempting one-shot generation of all files...")
    files_content = get_all_files_content(description, file_list)

    if files_content is None:
        # Fallback: generate files one by one passing previous files as context
        print("🔄 Falling back to sequential generation with context passing...")
        files_content = {}
        for rel_path in file_list:
            print(f"📝 Generating content for: {rel_path} with context of {len(files_content)} files")
            content = get_file_content_with_context(description, rel_path, files_content)
            files_content[rel_path] = content
    else:
        print("✅ One-shot generation successful.")

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
                    content = json.dumps(parsed_json, indent=2)
                except Exception as e:
                    print(f"⚠️ Warning: Could not parse extracted package.json content: {e}")
            else:
                print("⚠️ Warning: Could not extract a valid JSON object from package.json content.")

        write_file(file_path, content)

    print("✅ Project created successfully.")

# Utilities

def safe_run_command(cmd, cwd=None, max_retries=3):
    env = os.environ.copy()
    env["CI"] = "true"
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
    node_modules_path = os.path.join(base_path, 'node_modules')
    if os.path.exists(node_modules_path):
        print("🧹 Removing existing node_modules folder...")
        shutil.rmtree(node_modules_path)
    for lockfile in ['package-lock.json', 'yarn.lock']:
        lockfile_path = os.path.join(base_path, lockfile)
        if os.path.exists(lockfile_path):
            print(f"🧹 Removing existing {lockfile} file...")
            os.remove(lockfile_path)
