from gpt4all import GPT4All

model_path = "C:\\Users\\kmmay\\AppData\\Local\\nomic.ai\\GPT4All\\mistral-7b-instruct-v0.1.Q4_0.gguf"
gpt4all_model = GPT4All(model_path)

def chat_with_gpt(prompt):
    try:
        response = gpt4all_model.generate(prompt)
        return response
    except Exception as e:
        return f"Error: {e}"
