from github import Github
from groq import Groq
from agents import orchestrator
from dotenv import load_dotenv
import os
import re
from retriever import get_context
from scanner import update_on_pr
from database import save_review

load_dotenv()


github = Github(os.getenv("GITHUB_TOKEN"))
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_changed_func(patch):
   
    matches = re.findall(r'def (\w+)\(', patch)
    if matches:
        return matches[0]
    return None

def review_pr(repo_name, pr_number):
    
    
    repo = github.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    
    print(f"Reviewing PR: {pr.title}")
    
    
    print("\n🔄 Updating DB for changed files...")
    update_on_pr(repo_name, pr_number)
    
    
    files = pr.get_files()
    
    for file in files:
        
      
        if not file.filename.endswith(('.py', '.sql', '.js', '.java')):
            print(f"⏭️ Skipping: {file.filename}")
            continue
        
        print(f"\n📄 File: {file.filename}")
        
        if file.patch:
            
            
            func_name = extract_changed_func(file.patch)
            print(f"🔍 Changed function: {func_name}")
            
            if func_name:
              
                print("📦 Getting context from DB...")
                context = get_context(func_name, file.filename)
                
                if context:
                    print("✅ Context ready — using smart context!")
                else:
                   
                    print("⚠️ Context not found — using patch")
                    context = file.patch
            else:
                
                print("⚠️ No function found — using patch")
                context = file.patch
            
          
            print("🤖 Running AI review...")
            report = orchestrator(context)
            print(f"Review:\n{report}")
            
            
            pr.create_issue_comment(
                f"## AI Code Review 🤖\n**File:** `{file.filename}`\n\n{report}"
            )
            print(f"✅ Comment posted!")
            
           
            save_review(repo_name, pr_number,
                       file.filename, "CRITICAL", report)
            print("✅ Saved in LiteSQL!")

