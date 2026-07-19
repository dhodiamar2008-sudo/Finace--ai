"""Quick terminal chat client. Run with: python -m app.cli"""

from app.database import init_db
from app.auth import login, signup
from app.agent.gemini_agent import chat


def authenticate():
    print("1) Login  2) Sign up")
    choice = input("> ").strip()
    email = input("Email: ").strip()
    password = input("Password: ").strip()
    if choice == "2":
        name = input("Name: ").strip()
        result = signup(email, name, password)
    else:
        result = login(email, password)

    if result["status"] == "error":
        print(f"Error: {result['message']}")
        return authenticate()
    return result


def main():
    init_db()
    print("FinPilot AI — Personal Finance Agent (Gemini 2.5 Flash)\n")
    user = authenticate()
    print(f"\nWelcome, {user['name']}! Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            break
        if not user_input:
            continue
        reply = chat(user["user_id"], user_input)
        print(f"AI: {reply}\n")


if __name__ == "__main__":
    main()
