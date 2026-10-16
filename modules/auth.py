"""Authentication and password security module."""

import hashlib
import hmac
import os
import re
import sqlite3
from database.db import create_student, get_student, get_student_by_email, update_student


EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def hash_password(password: str, salt: bytes | None = None) -> str:
    """Hash password using PBKDF2-HMAC-SHA256 with a unique salt."""
    if not isinstance(password, str) or not password:
        raise ValueError("Password cannot be empty.")
    if salt is None:
        salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return f"{salt.hex()}:{dk.hex()}"


def verify_password(password: str, stored_hash: str | None) -> bool:
    """Verify password against stored salt:hash string."""
    if not stored_hash or not isinstance(password, str):
        return False
    try:
        parts = stored_hash.split(":")
        if len(parts) != 2:
            return False
        salt = bytes.fromhex(parts[0])
        expected_dk = bytes.fromhex(parts[1])
        calculated_dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
        return hmac.compare_digest(expected_dk, calculated_dk)
    except Exception:
        return False


def validate_email_format(email: str) -> str:
    """Validate and clean email address."""
    clean_email = email.strip() if isinstance(email, str) else ""
    if not clean_email:
        raise ValueError("Email address cannot be empty.")
    if not EMAIL_REGEX.match(clean_email):
        raise ValueError("Please provide a valid email address (e.g. name@example.com).")
    return clean_email.lower()


def register_user(name: str, email: str, password: str, confirm_password: str) -> int:
    """Register a new student with email and password."""
    clean_name = name.strip() if isinstance(name, str) else ""
    if not clean_name:
        raise ValueError("Full name cannot be empty.")

    clean_email = validate_email_format(email)

    if not password:
        raise ValueError("Password cannot be empty.")
    if len(password) < 6:
        raise ValueError("Password must be at least 6 characters long.")
    if password != confirm_password:
        raise ValueError("Passwords do not match.")

    existing = get_student_by_email(clean_email)
    if existing:
        raise ValueError("An account with this email already exists. Please log in.")

    pwd_hash = hash_password(password)
    student_id = create_student(clean_name, clean_email, password_hash=pwd_hash)
    return student_id


def authenticate_user(email: str, password: str) -> sqlite3.Row:
    """Authenticate student by email and password."""
    clean_email = validate_email_format(email)
    if not password:
        raise ValueError("Password cannot be empty.")

    student = get_student_by_email(clean_email)
    if not student:
        raise ValueError("No account found with this email. Please register first.")

    stored_hash = student["password_hash"] if "password_hash" in student.keys() else None
    if not stored_hash or not verify_password(password, stored_hash):
        raise ValueError("Incorrect password. Please try again.")

    return student
