from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def classify_severity(review_report):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": """Classify issues by severity.
Only include issues from the report.
No new issues.

Format:
## 🎯 Severity
🔴 CRITICAL: [issue - 1 line]
🟡 MEDIUM: [issue - 1 line]
🟢 LOW: [issue - 1 line]
Total: X (C:X M:X L:X)"""
            },
            {
                "role": "user",
                "content": f"Classify:\n{review_report}"
            }
        ]
    )
    return response.choices[0].message.content

