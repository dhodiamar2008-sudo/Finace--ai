"""
Simple auth using stdlib hashlib (PBKDF2-HMAC-SHA256) so we avoid extra
native dependencies (like bcrypt) that can be finicky to install on Windows.
Good enough for a personal/portfolio project; swap for a proper auth
provider (Auth0, Firebase Auth, etc.) before any real production use.
"""

import hashlib
import hmac
import os

from app.database import SessionLocal, User

ITERATIONS = 200_000


def _hash_password(password: str, salt: bytes | None = None) -> str:
    salt = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITERATIONS)
    return f"{salt.hex()}${digest.hex()}"


def _verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, digest_hex = stored.split("$")
    except ValueError:
        return False
    salt = bytes.fromhex(salt_hex)
    new_digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITERATIONS)
    return hmac.compare_digest(new_digest.hex(), digest_hex)


def signup(email: str, name: str, password: str) -> dict:
    email = email.strip().lower()
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            return {"status": "error", "message": "An account with this email already exists."}

        user = User(email=email, name=name.strip(), password_hash=_hash_password(password))
        db.add(user)
        db.commit()
        db.refresh(user)
        return {"status": "ok", "user_id": user.id, "name": user.name, "email": user.email}
    finally:
        db.close()


def login(email: str, password: str) -> dict:
    email = email.strip().lower()
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user or not _verify_password(password, user.password_hash):
            return {"status": "error", "message": "Invalid email or password."}
        return {"status": "ok", "user_id": user.id, "name": user.name, "email": user.email}
    finally:
        db.close()
