from groq import Groq
from severity import classify_severity  # ye add karo upar
from dotenv import load_dotenv
from autofix import generate_fix
import os

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def ask_ai(system_prompt, code):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Review this code:\n{code}"}
        ]
    )
    return response.choices[0].message.content

def bug_agent(code):
    prompt = """You are a Bug Detection Expert.
Find ONLY real bugs. No assumptions.
Be specific about line/function.

Format:
🐛 BUG REPORT
- [function_name]: [exact bug in 1 line]

Max 3 bugs. If none: No bugs found ✅"""
    return ask_ai(prompt, code)


def security_agent(code):
    prompt = """You are a Security Expert.
Find ONLY real security issues. No assumptions.
Be specific about line/function.

Format:
🔒 SECURITY REPORT
- [function_name]: [exact issue in 1 line]

Max 3 issues. If none: No security issues ✅"""
    return ask_ai(prompt, code)

def performance_agent(code):
    prompt = """You are a Performance Expert.
Find ONLY real performance problems. No assumptions.
Be specific about line/function.

Format:
⚡ PERFORMANCE REPORT
- [function_name]: [exact problem in 1 line]

Max 3 problems. If none: No performance issues ✅"""
    return ask_ai(prompt, code)

def check_test_coverage(code):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": """You are a Test Coverage Expert.
List only functions WITHOUT tests.
Suggest 2 most important test cases only.

Format:
## 🧪 Test Coverage
❌ No tests: [function1, function2]
💡 Write tests for: [top 2 functions]
Coverage: ~X%"""
            },
            {
                "role": "user",
                "content": f"Check:\n{code}"
            }
        ]
    )
    return response.choices[0].message.content


def orchestrator(code):
    print("🐛 Running Bug Agent...")
    bugs = bug_agent(code)
    
    print("🔒 Running Security Agent...")
    security = security_agent(code)
    
    print("⚡ Running Performance Agent...")
    performance = performance_agent(code)

    print("🧪 Checking Test Coverage...")
    tests = check_test_coverage(code)
    
    # Sab milao
    combined = f"{bugs}\n\n{security}\n\n{performance}"
    
    # Severity classify karo
    print("🎯 Classifying Severity...")
    severity = classify_severity(combined)

    print("🔧 Generating Auto-fix...")
    autofix = generate_fix(code, combined)
    
    # Final report
    final_report = f"""# 🤖 AI Code Review Report

{bugs}

{security}

{performance}

{tests}
---

{severity}
---

{autofix}

---

*Reviewed by DeepReview AI*"""
    
    return final_report