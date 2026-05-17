<div align="center">

# 🔍 deepReview AI

### AI Powered Code Review Agent

**Next-generation code review using Multi-Agent LLM Analysis & Vector Memory**

**Python 3.10+** | **Groq** | **Flask** | **LiteSQL** | **ChromaDB** | **MIT License**

</div>

---

## 📌 Overview

**deepReview AI** is an intelligent, AI-powered Pull Request review system built for modern development teams. It replaces traditional manual code reviews with a seamless blend of **multi-agent LLM analysis**, **vector memory**, and **automatic GitHub commenting** — making every PR review instant, accurate, and completely automated.

Whether you're a solo developer or working with a large team — deepReview AI watches every PR so you don't have to.

---

## ✨ Features

### 👨‍💻 For Developers

| Feature | Description |
|---|---|
| 🐛 **Bug Detection Agent** | Automatically detects logic errors, null pointers, and unhandled edge cases |
| 🔒 **Security Analysis Agent** | Scans for SQL injection, XSS, hardcoded secrets, and known vulnerabilities |
| ⚡ **Performance Agent** | Identifies slow queries, memory leaks, and inefficient loops |
| 🎨 **Code Style Agent** | Checks naming conventions, formatting, and language-specific best practices |
| 💬 **Auto PR Comments** | Posts a structured, actionable review directly on the GitHub PR once analysis completes |

### 🧠 For Teams

| Feature | Description |
|---|---|
| 🧬 **Vector Memory** | Stores past reviews in ChromaDB — recalls similar patterns for smarter suggestions |
| 📈 **Self-Learning** | Learns your team's coding style and avoids repeating the same feedback |
| 📊 **Analytics Dashboard** | PR history, issue trends, and team leaderboard — all in one place |
| 🚦 **CI/CD Integration** | Blocks merge on critical issues; auto-approves clean PRs via status checks |

---

## 🔄 How It Works

```
Step 01 → PR Opened          Developer opens a Pull Request on GitHub
Step 02 → Webhook Fires      GitHub sends an event to the deepReview AI server
Step 03 → Multi-Agent Run    Bug, Security, Performance, and Style agents run in parallel
Step 04 → Groq LLM Analysis  Each agent analyzes the code diff using Groq's fast LLM
Step 05 → Severity Tag       Issues are classified as Critical / High / Medium / Low / Info
Step 06 → PR Comment Posted  A structured review is automatically posted as a PR comment
Step 07 → Merge Decision     Critical issues = Merge blocked | Clean PR = Green status check
```

---

## 📊 Severity Classification

```
🔴 CRITICAL  →  Security vulnerabilities, data-loss bugs     (merge blocked)
🟠 HIGH      →  Logic errors, broken functionality           (merge blocked)
🟡 MEDIUM    →  Performance issues, deprecated usage         (warning only)
🟢 LOW       →  Style issues, minor improvements             (suggestion)
🔵 INFO      →  Best practice tips, optional enhancements    (informational)
```

---

## 🛠️ Tech Stack

```
LLM Engine      →  Groq (Llama 3 / Mixtral)       Blazing fast inference — PR reviewed in under 30s
Webhook Server  →  Flask                           Receives and routes incoming GitHub events
Database        →  LiteSQL (custom)                Stores reviews, PR history, and fix tracking
Vector DB       →  ChromaDB                        Semantic search over past reviews & code patterns
GitHub Layer    →  PyGitHub + REST API              Reads PRs, posts comments, sets status checks
Dashboard       →  Streamlit                        Stats, leaderboard, and trends UI
CI/CD Hook      →  GitHub Actions / Status Checks  Controls merge based on issue severity
```

---

## 📁 Project Structure

```
deepreview-ai/
│
├── main.py                        # Entry point — starts the server
│
├── agents/
│   ├── orchestrator.py            # Coordinates all agents
│   ├── bug_detector.py            # Bug detection agent
│   ├── security_agent.py          # Security analysis agent
│   ├── performance_agent.py       # Performance optimization agent
│   └── style_agent.py             # Code style checker agent
│
├── core/
│   ├── groq_client.py             # Groq LLM wrapper
│   ├── github_client.py           # GitHub API integration
│   ├── webhook_handler.py         # Incoming webhook processor
│   └── severity_classifier.py    # Issue severity tagging logic
│
├── db/
│   ├── litesql.py                 # LiteSQL DB handler (custom)
│   ├── models.py                  # Review, PR, and Issue models
│   └── chroma_store.py            # ChromaDB vector operations
│
├── dashboard/
│   └── app.py                     # Streamlit analytics dashboard
│
├── scripts/
│   └── init_db.py                 # Database initialization script
│
└── data/
    ├── deepreview.db              # LiteSQL database file
    └── chroma/                    # ChromaDB persistent store
```

---

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/deepreview-ai.git
cd deepreview-ai
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Fill in your `.env` file:

```env
# Groq LLM
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx
GROQ_MODEL=llama3-70b-8192

# GitHub
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
GITHUB_WEBHOOK_SECRET=your_webhook_secret

# Database
DB_PATH=./data/deepreview.db
CHROMA_PERSIST_DIR=./data/chroma

# Feature Flags
BLOCK_MERGE_ON_CRITICAL=true
AUTO_APPROVE_PERFECT=false
```

### 5. Initialize the Database

```bash
python scripts/init_db.py
```

### 6. Run the App

```bash
# Start Flask webhook server
python main.py

# In a new terminal, start Streamlit dashboard
streamlit run dashboard/app.py
```

---

## 🔗 GitHub Webhook Setup

1. Go to your GitHub repository → **Settings → Webhooks → Add webhook**

2. Fill in the details:
   ```
   Payload URL:   https://your-server.com/webhook
   Content type:  application/json
   Secret:        (same as GITHUB_WEBHOOK_SECRET in .env)
   ```

3. Select these events:
   - ✅ Pull requests
   - ✅ Pull request reviews
   - ✅ Statuses

4. Click **Add webhook**

> **For local development:** Use [ngrok](https://ngrok.com) to expose your local server
> ```bash
> ngrok http 8000
> # Paste the generated URL as your Payload URL
> ```

---

## 📦 Requirements

```txt
flask
streamlit
groq
PyGitHub
chromadb
requests
python-dotenv
numpy
pandas
```

---

## 🔐 Security & Privacy

- Never hardcode your Groq API key or GitHub token in source code — use `.env` only
- Always add `.env` to your `.gitignore`
- Every incoming webhook request is verified using the webhook secret — unauthorized requests are rejected
- The LiteSQL database file is stored locally — sensitive review data never leaves your machine

---

## 💬 Sample PR Comment

```
🤖 deepReview AI Analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Summary: 1 critical · 1 medium · 2 suggestions found

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔴 CRITICAL — Security Issue
File: auth/login.py | Line: 47

User input is being injected directly into an SQL query.
SQL Injection vulnerability detected.

  ❌ query = f"SELECT * FROM users WHERE id='{user_id}'"
  ✅ query = "SELECT * FROM users WHERE id=?"
     cursor.execute(query, (user_id,))

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🟡 MEDIUM — Performance Issue
File: api/posts.py | Line: 89

N+1 query problem detected — a DB call is made inside a loop.
Use batch fetching or select_related() instead.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Merge Status: BLOCKED (Critical issues present)
🕐 Analysis time: 21.4s  |  Powered by deepReview AI
```

---

## 🗂️ Database Schema (LiteSQL)

```sql
-- Pull Requests
pull_requests (id, repo, pr_number, author, title, created_at, status)

-- Reviews
reviews (id, pr_id, agent, severity, file, line, message, suggestion, created_at)

-- Fix Tracking
fix_logs (id, review_id, was_fixed, fixed_at)

-- Team Preferences
team_rules (id, repo, rule_type, rule_value, created_at)
```

---

## 🗺️ Roadmap

- [x] **Week 1** — Core agent: GitHub webhook + basic PR analysis + auto comment
- [x] **Week 2** — Multi-agent system + severity classification + test coverage detection
- [x] **Week 3** — Learning system (LiteSQL + ChromaDB) + auto-fix suggestions + dashboard
- [x] **Week 4** — Multi-language support + CI/CD integration + performance optimization

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add: your feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request — deepReview AI will review it automatically 😄

---



<div align="center">

**🌟 Star this repo if deepReview AI caught a bug before you did!**

[Report Bug](https://github.com/yourusername/deepreview-ai/issues) · [Request Feature](https://github.com/yourusername/deepreview-ai/issues)

**deepReview AI** — *The code reviewer that never sleeps* 🌙

</div>
