"""
PKCE (Proof Key for Code Exchange) Helper Functions

Implements RFC 7636 for OAuth 2.0 PKCE flow.
"""

import base64
import hashlib
import secrets


def generate_code_verifier(length: int = 64) -> str:
    """
    Generate a cryptographically random code verifier.

    Args:
        length: Length of code verifier (43-128 characters, default: 64)

    Returns:
        Base64URL-encoded random string

    Raises:
        ValueError: If length is outside valid range (43-128)
    """
    if length < 43 or length > 128:
        raise ValueError("Code verifier length must be between 43 and 128 characters")

    # Generate random bytes and encode as base64url
    random_bytes = secrets.token_bytes(length)
    # Base64URL encoding (RFC 4648 Section 5)
    verifier = base64.urlsafe_b64encode(random_bytes).decode("utf-8").rstrip("=")
    # Ensure it meets length requirement
    if len(verifier) < 43:
        # Pad if needed (shouldn't happen with proper length, but safety check)
        verifier = verifier + "A" * (43 - len(verifier))
    return verifier[:length]  # Trim to exact length


def generate_code_challenge(verifier: str, method: str = "S256") -> str:
    """
    Generate code challenge from code verifier.

    Args:
        verifier: Code verifier string
        method: Challenge method ("S256" for SHA256, "plain" for no transformation)

    Returns:
        Base64URL-encoded code challenge

    Raises:
        ValueError: If method is not "S256" or "plain"
    """
    if method == "S256":
        # SHA256 hash and base64url encode
        sha256_hash = hashlib.sha256(verifier.encode("utf-8")).digest()
        challenge = base64.urlsafe_b64encode(sha256_hash).decode("utf-8").rstrip("=")
        return challenge
    elif method == "plain":
        # No transformation (not recommended for security)
        return verifier
    else:
        raise ValueError(f"Unsupported code challenge method: {method}")


def verify_code_verifier(verifier: str, challenge: str, method: str = "S256") -> bool:
    """
    Verify that code verifier matches code challenge.

    Args:
        verifier: Code verifier to verify
        challenge: Expected code challenge
        method: Challenge method used ("S256" or "plain")

    Returns:
        True if verifier matches challenge, False otherwise
    """
    try:
        expected_challenge = generate_code_challenge(verifier, method)
        return expected_challenge == challenge
    except Exception:
        return False


def generate_pkce_pair(length: int = 64, method: str = "S256") -> tuple[str, str]:
    """
    Generate both code verifier and code challenge.

    Args:
        length: Length of code verifier (43-128 characters, default: 64)
        method: Challenge method ("S256" for SHA256)

    Returns:
        Tuple of (code_verifier, code_challenge)
    """
    verifier = generate_code_verifier(length)
    challenge = generate_code_challenge(verifier, method)
    return verifier, challenge
