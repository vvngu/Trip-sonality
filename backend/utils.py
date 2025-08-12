import os

def load_prompt(file: str) -> str:
    path = os.path.join("prompts", f"{file}.txt")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    except Exception as e:
        print(f"Error loading Prompt file {path} error: {e}")
        return "You are a helpful AI assistant."
    

def clean_json_content(raw: str) -> str:
    print(raw)
    raw = raw.split("TERMINATE")[0].strip()
    if raw.startswith("```json"):
        raw = raw[len("```json"):].strip()
    if raw.endswith("```"):
        raw = raw[:-3].strip()
    return raw
