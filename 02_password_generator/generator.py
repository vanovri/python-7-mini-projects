import secrets
import string
from typing import Dict, Any

try:
    import pyperclip
except ImportError:
    pyperclip = None


def generate_password(
    length: int = 16,
    use_uppercase: bool = True,
    use_lowercase: bool = True,
    use_digits: bool = True,
    use_symbols: bool = True,
) -> str:
    if length < 4:
        raise ValueError("Password length must be at least 4 characters.")

    pools = []
    if use_uppercase:
        pools.append(string.ascii_uppercase)
    if use_lowercase:
        pools.append(string.ascii_lowercase)
    if use_digits:
        pools.append(string.digits)
    if use_symbols:
        pools.append("!@#$%^&*()-_=+[]{}|;:,.<>?")

    if not pools:
        raise ValueError("At least one character set must be enabled.")

    # Guarantee at least one character from each selected character set
    password_chars = [secrets.choice(pool) for pool in pools]
    all_chars = "".join(pools)
    password_chars.extend(secrets.choice(all_chars) for _ in range(length - len(pools)))

    # Cryptographically shuffle using secrets.SystemRandom
    secrets.SystemRandom().shuffle(password_chars)
    return "".join(password_chars)


def check_strength(password: str) -> Dict[str, Any]:
    has_upper = any(c in string.ascii_uppercase for c in password)
    has_lower = any(c in string.ascii_lowercase for c in password)
    has_digit = any(c in string.digits for c in password)
    has_symbol = any(c in "!@#$%^&*()-_=+[]{}|;:,.<>?" for c in password)

    variety = sum([has_upper, has_lower, has_digit, has_symbol])
    score = 0
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    if len(password) >= 16:
        score += 1
    score += variety  # max 7

    if score >= 6:
        label = "Strong"
    elif score >= 4:
        label = "Medium"
    else:
        label = "Weak"

    return {
        "length": len(password),
        "has_upper": has_upper,
        "has_lower": has_lower,
        "has_digit": has_digit,
        "has_symbol": has_symbol,
        "score": score,
        "max_score": 7,
        "rating": label,
    }


def copy_to_clipboard(text: str) -> bool:
    if pyperclip is None:
        return False
    try:
        pyperclip.copy(text)
        return True
    except Exception:
        return False
