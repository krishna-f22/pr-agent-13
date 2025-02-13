from groq import Groq
import json

client = Groq(api_key="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")


def read_python_file(file_path):

    with open(file_path, "r", encoding="utf-8") as file:
        lines = [f"{i}: {line.rstrip()}" for i, line in enumerate(file, start=1)]

    return "\n".join(lines)


def ai_verify(content):

    # code = read_python_file(filepath)
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": """Return only the comments indicating what is wrong and the corresponding line number of the bug. 
                Do not include the corrected code or explanations beyond the comments. 
                Avoid extra formatting like triple backticks.
                Must follow the format of example output
                Example output: 
                 { "line_number":1, "comment": "this is a bug"}""",
            },
            {"role": "user", "content": content},
        ],
        model="llama-3.1-8b-instant",
        temperature=0.1,
        max_completion_tokens=1024,
        top_p=1,
        stop=None,
        stream=False,
    )
    output = chat_completion.choices[0].message.content
    comments = [json.loads(line) for line in output.split("\n")]

    return comments


def read_python_file(file_path):

    with open(file_path, "r", encoding="utf-8") as file:
        lines = [f"{i}: {line.rstrip()}" for i, line in enumerate(file, start=1)]

    return "\n".join(lines)


# print(ai_verify("/home/team/code/git-pr/pr_diffs/cal.py"))
