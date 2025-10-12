"""ID generation utilities."""

import secrets
import string


def generate_token(length: int = 32) -> str:
    """Generate a secure random token."""
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def generate_alias_token() -> str:
    """Generate an alias token for virtual cards."""
    return f"stc_{generate_token(24)}"


def generate_pan_last4() -> str:
    """Generate a fake PAN last 4 digits."""
    return "".join(secrets.choice(string.digits) for _ in range(4))

