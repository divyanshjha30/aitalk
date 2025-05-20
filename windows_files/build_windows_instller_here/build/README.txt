AITalk - AI-Powered Project Assistant for Windows
=================================================

AITalk is a command-line tool that leverages LLMs (Large Language Models) to help you:
- Create new React projects from a prompt
- Summarize and explain code files
- Chat interactively with an AI assistant
- Generate Git summaries and more

This project is designed for Windows and can be used as a standalone executable or via Python.

-------------------------------------------------
Features
-------------------------------------------------
- **Project Creation:** Generate a full React project from a simple description.
- **Chat Mode:** Interactive chat with an AI assistant.
- **Explain Code:** Get explanations for code snippets or files.
- **Summarize Files:** Summarize the contents of any text file.
- **Git Summary:** Generate summaries of your Git repository.

-------------------------------------------------
Installation
-------------------------------------------------
### Using the Installer
1. Run `AITalkInstaller.exe` and follow the prompts.
2. The installer will add AITALK to your system PATH for easy access.

### Manual Setup (Development)
1. Clone or extract this repository.
2. Open a terminal in the `windows` folder.
3. Create a virtual environment:
   ```
   python -m venv .venv
   ```
4. Activate the virtual environment:
   ```
   .venv\Scripts\activate
   ```
5. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
6. Set your Groq API key in the `.env` file:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```

-------------------------------------------------
Usage
-------------------------------------------------
You can run AITALK from any terminal:

- Create a new project:
  ```
  aitalk --create-project "make a react app"
  ```

- Explain code:
  ```
  aitalk --explain-5
  ```

- Chat mode:
  ```
  aitalk --chat
  ```

- Git summary:
  ```
  aitalk --git-summary
  ```

- Summarize a file:
  ```
  aitalk --summarise "summarise this file" file.txt
  ```

For help:
```
aitalk --help
```

-------------------------------------------------
Building a Standalone Executable
-------------------------------------------------
1. Activate your virtual environment.
2. Run:
   ```
   pyinstaller --onefile --name aitalk aitalk.py
   ```
3. The executable will be in the `dist` folder.

-------------------------------------------------
License
-------------------------------------------------
See LICENSE.txt for license information.

-------------------------------------------------
Credits
-------------------------------------------------
Developed by Divyansh.
Powered by Groq LLM API.

-------------------------------------------------
Support
-------------------------------------------------
For issues or feature requests, please contact the author or open an issue on the repository.