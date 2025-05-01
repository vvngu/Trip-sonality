import os

# --- Prompt 加载函数 ---
def load_prompt(file: str) -> str:
    """从 prompts 文件夹加载指定文件的内容作为 Agent 的系统提示。"""
    path = os.path.join("backend", "prompts", f"{file}.txt")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    except Exception as e:
        print(f"加载 Prompt 文件 {path} 时出错: {e}")
        return "You are a helpful AI assistant."
    

def clean_json_content(raw: str) -> str:
    print(raw)
    raw = raw.split("TERMINATE")[0].strip()
    if raw.startswith("```json"):
        raw = raw[len("```json"):].strip()
    if raw.endswith("```"):
        raw = raw[:-3].strip()
    return raw
