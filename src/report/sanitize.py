"""Sensitive data sanitization for report output.

Provides a strict guardrail that prevents passwords, API keys, tokens, secrets,
and other sensitive information from appearing in the final HTML report.

Two detection strategies are applied recursively to all agent result data:

1. **Key-based detection**: If a dict key matches a known sensitive field name
   (e.g. "password", "secret_key", "api_token"), the value is fully redacted.

2. **Pattern-based detection**: String values are scanned for inline secrets
   such as connection strings with embedded passwords, AWS access keys, JWTs,
   bearer tokens, and high-entropy hex/base64 strings that look like secrets.

All functions are pure -- no side effects, no IO.
"""

from __future__ import annotations

import re
from typing import Any

REDACTED = "[REDACTED]"

# ---------------------------------------------------------------------------
# Key-based detection: dict keys that indicate sensitive values
# ---------------------------------------------------------------------------

_SENSITIVE_KEY_FRAGMENTS: frozenset[str] = frozenset({
    "password",
    "passwd",
    "pwd",
    "secret",
    "api_key",
    "apikey",
    "api_secret",
    "access_key",
    "secret_key",
    "private_key",
    "auth_token",
    "access_token",
    "refresh_token",
    "bearer",
    "credential",
    "credentials",
    "connection_string",
    "conn_str",
    "database_url",
    "db_password",
    "db_url",
    "encryption_key",
    "signing_key",
    "client_secret",
    "oauth_token",
    "jwt",
    "session_secret",
    "cookie_secret",
})


def _is_sensitive_key(key: str) -> bool:
    """Check whether a dict key indicates its value is sensitive."""
    normalized = key.lower().strip()
    return any(fragment in normalized for fragment in _SENSITIVE_KEY_FRAGMENTS)


# ---------------------------------------------------------------------------
# Pattern-based detection: regex patterns for inline secrets in strings
# ---------------------------------------------------------------------------

_SECRET_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    # Passwords in connection strings / URLs: ://user:pass@host
    (re.compile(r"(://[^:/?#]+:)[^@/?#]+(@)"), r"\1" + REDACTED + r"\2"),
    # password=value in query strings or config
    (re.compile(
        r"((?:password|passwd|pwd|secret|api_key|apikey|token|auth)"
        r"\s*[=:]\s*)[\"']?[^\s\"',;}{)]+",
        re.IGNORECASE,
    ), r"\1" + REDACTED),
    # AWS access key IDs (AKIA...)
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), REDACTED),
    # AWS secret keys (40-char base64)
    (re.compile(r"(?<=[=:\s\"\'])[A-Za-z0-9/+=]{40}(?=[\"\';\s,}]|$)"), REDACTED),
    # Bearer tokens in text
    (re.compile(r"(Bearer\s+)\S+", re.IGNORECASE), r"\1" + REDACTED),
    # JWT tokens (three base64url segments separated by dots)
    (re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"), REDACTED),
    # GitHub personal access tokens
    (re.compile(r"\bgh[ps]_[A-Za-z0-9_]{36,}\b"), REDACTED),
    # Generic hex secrets (32+ hex chars, commonly API keys)
    (re.compile(r"\b[0-9a-fA-F]{32,}\b"), REDACTED),
    # SSH private key markers
    (re.compile(r"-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----[\s\S]*?-----END\s+(RSA\s+)?PRIVATE\s+KEY-----"), REDACTED),
]


def _redact_patterns(value: str) -> str:
    """Scan a string for known secret patterns and redact matches."""
    result = value
    for pattern, replacement in _SECRET_PATTERNS:
        result = pattern.sub(replacement, result)
    return result


# ---------------------------------------------------------------------------
# Recursive sanitization
# ---------------------------------------------------------------------------


def sanitize_value(value: Any) -> Any:
    """Recursively sanitize a value, redacting sensitive data.

    - Dicts: check keys for sensitive names, recurse into values
    - Lists/tuples: recurse into each element
    - Strings: scan for inline secret patterns
    - Other types: pass through unchanged
    """
    if isinstance(value, dict):
        return {
            k: REDACTED if _is_sensitive_key(k) else sanitize_value(v)
            for k, v in value.items()
        }
    if isinstance(value, list):
        return [sanitize_value(item) for item in value]
    if isinstance(value, tuple):
        return tuple(sanitize_value(item) for item in value)
    if isinstance(value, str):
        return _redact_patterns(value)
    return value


def sanitize_agent_results(
    agent_results: dict[str, Any],
) -> dict[str, Any]:
    """Sanitize all agent results, removing sensitive data before rendering.

    This is the main entry point called from the pipeline. It walks through
    every agent's serialized data and applies both key-based and pattern-based
    redaction.

    Pure function: returns a new dict, does not mutate the input.
    """
    return {
        agent_key: sanitize_value(agent_data)
        for agent_key, agent_data in agent_results.items()
    }
