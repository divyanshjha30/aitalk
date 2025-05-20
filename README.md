# 🧠 aitalk

**aitalk** is a powerful AI-driven command-line assistant for developers. It leverages LLMs (via Groq API) to automate project scaffolding, explain shell commands, summarize files, provide git insights, and even chat interactively—all from your terminal.

---

## 🚀 Features

- **Project Creation:**  
  Instantly scaffold production-ready React projects from a simple description.

- **Command Explanation:**  
  Explain the last _N_ shell commands and their outputs using LLMs.

- **File Summarization:**  
  Summarize `.txt`, `.pdf`, or `.docx` files with a custom prompt.

- **Git Summary:**  
  Get a human-readable, technical summary of your current git repository.

- **Interactive Chat:**  
  Chat with an LLM in your terminal for brainstorming, troubleshooting, or learning.

---

## 🛠️ Installation & Setup

### 1. **Clone the Repository**

```zsh
git clone <your-repo-url>
cd aitalk
```

### 2. **Set Up Python Virtual Environment**

```zsh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. **Configure Groq API Key**

Create a [`.env`](.env) file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

### 4. **(Optional) Install CLI Wrapper**

You can use the provided Bash script as a CLI wrapper.  
Make it executable and add it to your PATH:

```zsh
chmod +x "bash script"
ln -s "$(pwd)/bash script" /usr/local/bin/aitalk
```

---

## 🖥️ Usage

### **Project Creation**

```zsh
aitalk --create-project "make a react app with login and dashboard"
```
- Generates a full React project based on your description.
- Handles file structure, content, and even `npm install` and `git init`.

---

### **Explain Last N Commands**

```zsh
aitalk --explain-5
```
- Explains the last 5 shell commands and their outputs.
- Reads from your terminal session log (default: `~/aitalk_session.log`).

> **Tip:** Start your terminal session with:
> ```zsh
> script ~/aitalk_session.log
> ```
> to enable command logging.

---

### **Summarize a File**

```zsh
aitalk --summarise "summarise this file for a non-technical audience" file.txt
```
- Supports `.txt`, `.pdf`, and `.docx` files.
- Uses LLMs to generate a summary based on your prompt.

---

### **Git Summary**

```zsh
aitalk --git-summary
```
- Summarizes your current git repository’s status and history.

---

### **Interactive Chat**

```zsh
aitalk --chat
```
- Opens a conversational chat with the LLM in your terminal.

---

### **Help**

```zsh
aitalk --help
```
- Prints usage instructions.

---

## 🧩 Project Structure

```
aitalk/
├── aitalk.py                # Main CLI entry point
├── bash script              # Bash wrapper for CLI usage
├── .env                     # Groq API key
├── requirements.txt         # Python dependencies
├── project_builder.py       # Project scaffolding logic
├── explain_utils.py         # Command explanation logic
├── summarise_utils.py       # File summarization logic
├── chat_utils.py            # Interactive chat logic
├── git_summary_utils.py     # Git summary logic
├── groq_client.py           # Groq API integration
├── llm_utils.py             # (Optional) Local LLM integration
├── system_utils.py          # Filesystem and command helpers
└── ...
```

---

## ⚙️ How It Works

- **Bash Script:**  
  Handles argument parsing, environment checks, and delegates to the Python backend.

- **Python Backend:**  
  - **aitalk.py:** Parses CLI arguments and dispatches to the correct feature.
  - **Groq API:** All LLM-powered features use the Groq API for fast, accurate responses.
  - **Logging:** For command explanation, reads from a session log (e.g., `~/aitalk_session.log`).

---

## 📝 Logging Shell Commands for Explanation

To use the `--explain-X` feature, you must log your shell session:

```zsh
script ~/aitalk_session.log
```
Then use your terminal as usual.  
When you want explanations, run:

```zsh
aitalk --explain-5
```

---

## 🧑‍💻 Developer Notes

- **Extending:**  
  Add new features by updating the Bash script and `aitalk.py` dispatch logic.
- **API Models:**  
  Model selection is handled in `groq_client.py` via `TASK_MODEL_MAP`.
- **Error Handling:**  
  The system is robust to API/network errors and will retry or provide actionable messages.

---

## 🛡️ Security

- **API Key:**  
  Never commit your `.env` file or API key to version control.
- **Dependencies:**  
  Review and update dependencies regularly.

---

## 🤝 Contributing

Pull requests and issues are welcome!  
Please open an issue for bugs, feature requests, or questions.

---

## 📄 License

MIT License (or your preferred license here)

---

## 🙏 Acknowledgements

- [Groq](https://groq.com/) for blazing-fast LLM inference.
- [OpenAI](https://openai.com/) for inspiration.
- All contributors and users!

---

**Happy hacking with aitalk! 🚀**
