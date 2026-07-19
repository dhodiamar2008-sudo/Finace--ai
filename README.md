# FinPilot AI — Personal Finance Agent

Agentic + Generative + ML personal finance assistant, powered by **Gemini 2.5 Flash**.

## What it does
- **Multi-user accounts** with email/password login (each user's data is fully isolated).
- **Persistent conversation memory** — stored in the database, survives app restarts.
- **Agentic layer**: Gemini decides when to log a transaction, check budgets,
  create savings goals, track bills, pull a forecast, or scan for anomalies —
  via real function calling, not a single static prompt.
- **Generative layer**: natural-language expense logging ("I spent 500 on
  groceries yesterday") and personalized, numbers-based financial advice.
- **ML layer**:
  - Linear-trend forecasting of next month's spend per category.
  - Z-score anomaly detection on transactions.
  - Rule-based, fully explainable **Financial Health Score** (0–100) based on
    savings rate, income stability, budget discipline, and spending consistency.
- **Savings Goals** with progress tracking.
- **Bills & Subscriptions** tracker with monthly total.

## Setup (VS Code)

1. Open this folder in VS Code.
2. Create a virtual environment:
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Mac/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and add your Gemini API key
   (get one free at https://aistudio.google.com/apikey):
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` and make sure `GEMINI_API_KEY=` has your real key with
   no quotes and no extra spaces.

5. Run the web UI (Streamlit — from the project root, same folder as
   `requirements.txt`):
   ```bash
   streamlit run streamlit_app.py
   ```
   Sign up for an account, then try:
   - "I spent 500 rupees on groceries yesterday"
   - "I earned 50000 salary this month"
   - "How healthy are my finances?"
   - "I want to save ₹50000 for a laptop by December"
   - "Add my Netflix subscription, 500 rupees, due on the 5th"
   - "How much will I spend on groceries next month?"
   - "Any unusual transactions?"
   - "Set my food budget to 8000 per month"

6. Or run the CLI:
   ```bash
   python -m app.cli
   ```

7. Or run the API server:
   ```bash
   uvicorn app.main:app --reload
   ```
   Open http://127.0.0.1:8000/docs for interactive Swagger UI.

## Project structure
```
finance-ai/
├── app/
│   ├── main.py               # FastAPI server (auth + data + chat endpoints)
│   ├── cli.py                 # Terminal chat client with login
│   ├── config.py              # Env/config loader
│   ├── database.py            # SQLAlchemy models (User, Transaction, Budget,
│   │                           #   SavingsGoal, Bill, ChatMessage)
│   ├── auth.py                 # Signup/login (PBKDF2 password hashing, stdlib only)
│   ├── agent/
│   │   ├── gemini_agent.py    # Agentic orchestration + persistent memory
│   │   └── tools.py           # User-scoped tools the agent can call
│   └── ml/
│       ├── forecasting.py     # Forecasting + anomaly detection
│       └── insights.py        # Financial Health Score
├── data/                       # SQLite DB lives here
├── requirements.txt
└── .env.example
```

## Roadmap (not yet built)
This started from a larger spec (FinPilot AI full production build) that
included Next.js/Node/MongoDB, investment tracking, receipt OCR, and voice
commands. Those are intentionally deferred to keep this version simple,
working, and easy to run locally:
- **Phase 2**: Investment tracking (stocks/crypto/FD/etc.), Net Worth, asset
  allocation charts, auto-categorization confidence scoring.
- **Phase 3**: Receipt OCR (pytesseract), voice commands (speech_recognition),
  Google Sign-In, deployment to a real host (Render/Railway + a managed DB).

## Notes on security
Password hashing here (PBKDF2-HMAC-SHA256, stdlib `hashlib`) is fine for a
personal/portfolio project but is not a substitute for a real auth provider
before handling real users' financial data in production — no session
tokens/JWT/rate limiting are implemented yet.
