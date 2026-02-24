# helpers.py
# Reusable helper functions

import string
import random
from datetime import datetime, timezone

# ============================================
# SHORT CODE GENERATOR
# ============================================

# Characters we'll use in short codes
# Letters (upper and lower) + digits
CHARACTERS = string.ascii_letters + string.digits
# = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

def generate_short_code(length: int = 6) -> str:
    """
    Generate a random short code.

    Example:
        generate_short_code(6) → "aB3xY9"
        generate_short_code(4) → "k4sC"

    Args:
        length: How many characters (default 6)

    Returns:
        Random string of letters and numbers
    """
    return ''.join(random.choice(CHARACTERS) for _ in range(length))


# ============================================
# URL VALIDATOR
# ============================================

def is_valid_url(url: str) -> bool:
    """
    Check if URL starts with http:// or https://

    Args:
        url: The URL string to check

    Returns:
        True if valid, False if not
    """
    return url.startswith(('http://', 'https://'))


# ============================================
# EXPIRY CHECKER
# ============================================

def is_expired(expires_at) -> bool:
    """
    Check if a URL has expired.
    
    Must use timezone-aware datetime for comparison
    because PostgreSQL stores timestamps WITH timezone!
    """
    if expires_at is None:
        return False
    
    # datetime.now(timezone.utc) = timezone-AWARE current time
    # Both sides are now "aware" - comparison works!
    now = datetime.now(timezone.utc)
    
    return expires_at < now