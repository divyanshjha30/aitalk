# chat_utils.py

from groq_client import call_groq

def chat():
    print("💬 Interactive Chat Mode (type 'exit' or 'quit' to leave)")
    conversation_history = []

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ["exit", "quit"]:
            print("👋 Exiting chat mode.")
            break

        conversation_history.append({"role": "user", "content": user_input})

        # Build conversation string for LLaMA
        formatted_prompt = ""
        for message in conversation_history:
            if message["role"] == "user":
                formatted_prompt += f"User: {message['content']}\n"
            elif message["role"] == "assistant":
                formatted_prompt += f"Assistant: {message['content']}\n"

        # Call the Groq LLaMA model (let groq_client pick the right model)
        response = call_groq(
            prompt=formatted_prompt,
            task_type="chat"
        )

        print(f"Assistant: {response}\n")
        conversation_history.append({"role": "assistant", "content": response})
