#!/usr/bin/env python3

import sys
import re
from project_builder import build_project
from explain_utils import explain_last_n_commands_with_output

if __name__ == "__main__":
    if '--create-project' in sys.argv:
        idx = sys.argv.index('--create-project')
        if len(sys.argv) > idx + 1:
            desc = sys.argv[idx + 1]
            build_project(desc)
        else:
            print("❌ Missing project description.")
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
