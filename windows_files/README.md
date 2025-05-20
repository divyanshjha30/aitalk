# AITALK - AI-Powered Project Assistant for Windows

AITalk is a command-line tool that leverages LLMs (Large Language Models) to help you:

- Create new React projects from a prompt
- Summarize and explain code/files
- Chat interactively with an AI assistant
- Generate Git summaries and more

---

## Features

- **Project Creation:** Generate a full React project from a simple description.
- **Chat Mode:** Interactive chat with an AI assistant.
- **Explain Code:** Get explanations for code snippets or files.
- **Summarize Files:** Summarize the contents of any text, PDF, or DOCX file.
- **Git Summary:** Generate summaries of your Git repository.

---

## Installation (Windows)

1. **Clone or extract the repository.**
2. **Open a terminal in the `windows_files` folder.**
3. **Create a virtual environment:**
   ```cmd
   python -m venv .venv
   ```
4. **Activate the virtual environment:**
   ```cmd
   .venv\Scripts\activate
   ```
5. **Install dependencies:**
   ```cmd
   pip install -r requirements.txt
   ```
6. **Create a `.env` file in this directory and add your Groq API key:**
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

---

## Building a Standalone Installer (Optional)

1. **Download and install NSIS (Nullsoft Scriptable Install System):**
   [NSIS Download](https://nsis.sourceforge.io/Download)
2. **Go to `build_windows_instller_here\build` and follow the instructions in `instructions.txt` to build the Windows installer.**

---

## Usage

- **Create a new project:**
  ```cmd
  aitalk.bat --create-project "make a react app"
  ```
- **Explain last N commands:**
  ```cmd
  aitalk.bat --explain-5
  ```
- **Chat mode:**
  ```cmd
  aitalk.bat --chat
  ```
- **Git summary:**
  ```cmd
  aitalk.bat --git-summary
  ```
- **Summarize a file:**
  ```cmd
  aitalk.bat --summarise "summarise this file" file.txt
  ```
- **Help:**
  ```cmd
  aitalk.bat --help
  ```

---

## Security

- Never commit your .env file or API key to version control.
- Review and update dependencies regularly.

---

## License

See LICENSE.txt for license information.

---

## Support

For issues or feature requests, please contact the author or open an issue on the repository.
