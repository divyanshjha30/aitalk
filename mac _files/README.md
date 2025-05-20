# AITALK - AI-Powered Project Assistant for macOS

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

## Installation (macOS)

1. **Clone the repository:**
   ```sh
   git clone <your-repo-url>
   cd aitalk/mac _files
   ```
2. **Create a virtual environment and activate it:**
   ```sh
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
4. **Create a `.env` file in this directory and add your Groq API key:**
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```
5. **(Optional) Make the bash_script executable and add to your PATH:**
   ```sh
   chmod +x bash_script
   ln -s "$(pwd)/bash_script" /usr/local/bin/aitalk
   ```

---

## Usage

- **Create a new project:**
  ```sh
  aitalk --create-project "make a react app"
  ```
- **Explain last N commands:**
  ```sh
  aitalk --explain-5
  ```
- **Chat mode:**
  ```sh
  aitalk --chat
  ```
- **Git summary:**
  ```sh
  aitalk --git-summary
  ```
- **Summarize a file:**
  ```sh
  aitalk --summarise "summarise this file" file.txt
  ```
- **Help:**
  ```sh
  aitalk --help
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
