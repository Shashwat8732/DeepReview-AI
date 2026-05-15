from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_fix(code, issue):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": """You are a Code Fix Expert.
Fix ONLY the reported issues.
Show only changed lines.

Format:
## 🔧 Fix
❌ [function]: [problem]
✅ [fixed code - changed lines only]
💡 [what changed - 1 line]"""
            },
            {
                "role": "user",
                "content": f"Code:\n{code}\n\nFix these:\n{issue}"
            }
        ]
    )
    return response.choices[0].message.content
    
    