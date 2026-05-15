from flask import Flask, request, jsonify
from code_reviewer import review_pr

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def handle_webhook():
    
    
    
    data = request.json
    
   
    if "pull_request" not in data:
        return jsonify({"message": "Not a PR event"}), 200
    
  
    action = data.get("action")
    if action not in ["opened", "synchronize"]:
        return jsonify({"message": "Ignored"}), 200
    
   
    pr_number = data["pull_request"]["number"]
    repo_name = data["repository"]["full_name"]
    
    print(f"🔔 New PR detected: {repo_name} #{pr_number}")
    
    
    review_pr(repo_name, pr_number)
    
    return jsonify({"message": "Review done!"}), 200

if __name__ == "__main__":
    app.run(port=5001, debug=True)