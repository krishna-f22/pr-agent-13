from groq import Groq
import json
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def read_python_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return "".join(file.readlines())

def ai_verify(content):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": """Return JSON array of objects with line_number and comment. Example: [{"line_number":1, "comment": "bug here"}]""",
                },
                {"role": "user", "content": content},
            ],
            model="llama3-8b-8192",
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        output = chat_completion.choices[0].message.content
        return json.loads(output).get("comments", [])
    except json.JSONDecodeError:
        return []