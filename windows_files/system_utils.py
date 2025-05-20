import os
import subprocess

def make_dir(path):
    os.makedirs(path, exist_ok=True)

def write_file(filepath, content):
    with open(filepath, 'w') as f:
        f.write(content)

def run_command(command, cwd=None):
    print(f"👉 Running: {' '.join(command)} in {cwd or os.getcwd()}")
    result = subprocess.run(command, cwd=cwd)
    if result.returncode != 0:
        print(f"❌ Command failed: {' '.join(command)}")