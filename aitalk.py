import sys
import re
from project_builder import build_project
from explain_utils import explain_last_n_commands_with_output
from summarise_utils import summarise_file
from chat_utils import chat

if __name__ == "__main__":
    if '--create-project' in sys.argv:
        idx = sys.argv.index('--create-project')
        if len(sys.argv) > idx + 1:
            desc = sys.argv[idx + 1]
            build_project(desc)
        else:
            print("❌ Missing project description.")
    
    elif "--chat" in sys.argv:
        chat()

    elif '--summarise' in sys.argv:
        idx = sys.argv.index('--summarise')
        if len(sys.argv) > idx + 2:
            prompt = sys.argv[idx + 1]
            file_path = sys.argv[idx + 2]
            summarise_file(prompt, file_path)
        else:
            print("❌ Usage: aitalk --summarise \"prompt\" file.txt")
    else:
        explain_flag = None
        for arg in sys.argv:
            match = re.match(r'^--explain-(\d+)$', arg)
            if match:
                explain_flag = int(match.group(1))
                break
        
        if explain_flag is not None:
            explain_last_n_commands_with_output(explain_flag)
        else:
            print("Usage:")
            print("  aitalk --create-project \"build a react todo app\"")
            print("  aitalk --explain-5")
            print("  aitalk --summarise \"summarise this file\" file.txt")