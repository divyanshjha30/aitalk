import os
from groq_client import call_groq

def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".txt":
        with open(file_path, 'r') as f:
            return f.read()
    elif ext == ".pdf":
        try:
            import fitz  # PyMuPDF
        except ImportError:
            print("❌ PyMuPDF not installed. Run: pip install PyMuPDF")
            return None
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    elif ext == ".docx":
        try:
            from docx import Document
        except ImportError:
            print("❌ python-docx not installed. Run: pip install python-docx")
            return None
        doc = Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    else:
        print(f"❌ Unsupported file type: {ext}")
        return None

def summarise_file(prompt, file_path):
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    content = extract_text(file_path)
    if not content:
        print("❌ Could not extract text from file.")
        return
    llm_prompt = f"Summarize this file based on the following instruction: '{prompt}'.\n\nFile content:\n{content}"
    summary = call_groq(llm_prompt, task_type="summarize")
    print("------ Summary ------")
    print(summary)
    print("---------------------")