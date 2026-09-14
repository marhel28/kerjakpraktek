import json

path = r"C:\Users\Administrator\.gemini\antigravity-ide\brain\7e231fd4-35ab-48a1-a32b-6d63db5e1c7a\.system_generated\logs\transcript.jsonl"
with open(path, "r", encoding="utf-8") as f:
    for line in f:
        data = json.loads(line)
        if data.get("step_index") == 2851:
            print(data.get("content"))
