"""Unit tests for sensitive data sanitization.

Tests validate that the sanitization guardrail:
- Redacts values under sensitive dict keys (password, secret, token, etc.)
- Detects and redacts inline secrets in strings (connection strings, AWS keys,
  JWTs, bearer tokens, GitHub PATs, hex API keys)
- Recursively sanitizes nested dicts, lists, and tuples
- Preserves non-sensitive data unchanged
- Returns new structures without mutating the input
"""

import copy

import pytest

from src.report.sanitize import (
    REDACTED,
    _is_sensitive_key,
    _redact_patterns,
    sanitize_agent_results,
    sanitize_value,
)


# ---------------------------------------------------------------------------
# Key-based detection
# ---------------------------------------------------------------------------


class TestIsSensitiveKey:
    """Tests for _is_sensitive_key."""

    @pytest.mark.parametrize("key", [
        "password",
        "PASSWORD",
        "db_password",
        "api_key",
        "API_KEY",
        "apikey",
        "secret",
        "client_secret",
        "access_token",
        "auth_token",
        "refresh_token",
        "private_key",
        "secret_key",
        "access_key",
        "connection_string",
        "conn_str",
        "database_url",
        "db_url",
        "encryption_key",
        "signing_key",
        "oauth_token",
        "jwt",
        "session_secret",
        "cookie_secret",
        "bearer",
        "credential",
        "credentials",
        "  Password  ",
        "MY_API_KEY_VALUE",
        "user_password_hash",
    ])
    def test_detects_sensitive_keys(self, key: str) -> None:
        assert _is_sensitive_key(key) is True

    @pytest.mark.parametrize("key", [
        "file",
        "score",
        "severity",
        "name",
        "description",
        "category",
        "overall_score",
        "grade",
        "total_issues",
        "risk_level",
        "summary",
        "title",
        "effort",
        "priority",
        "rating",
    ])
    def test_ignores_safe_keys(self, key: str) -> None:
        assert _is_sensitive_key(key) is False


# ---------------------------------------------------------------------------
# Pattern-based detection
# ---------------------------------------------------------------------------


class TestRedactPatterns:
    """Tests for _redact_patterns on string values."""

    def test_redacts_password_in_connection_string(self) -> None:
        url = "postgresql://admin:s3cretP@ss@db.host:5432/mydb"
        result = _redact_patterns(url)
        assert "s3cretP@ss" not in result
        assert REDACTED in result
        assert "db.host:5432" in result

    def test_redacts_password_equals_value(self) -> None:
        config = "password=hunter2"
        result = _redact_patterns(config)
        assert "hunter2" not in result
        assert REDACTED in result

    def test_redacts_password_colon_value(self) -> None:
        config = "password: my_secret_value"
        result = _redact_patterns(config)
        assert "my_secret_value" not in result
        assert REDACTED in result

    def test_redacts_token_equals_value(self) -> None:
        config = "token=abc123xyz"
        result = _redact_patterns(config)
        assert "abc123xyz" not in result

    def test_redacts_aws_access_key(self) -> None:
        text = "Found hardcoded key AKIAIOSFODNN7EXAMPLE in config"
        result = _redact_patterns(text)
        assert "AKIAIOSFODNN7EXAMPLE" not in result
        assert REDACTED in result

    def test_redacts_bearer_token(self) -> None:
        text = "Authorization: Bearer eyABCDEFghijklmnop123"
        result = _redact_patterns(text)
        assert "eyABCDEFghijklmnop123" not in result
        assert "Bearer" in result
        assert REDACTED in result

    def test_redacts_jwt(self) -> None:
        jwt = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.abc123def456ghi789"
        result = _redact_patterns(jwt)
        assert jwt not in result
        assert REDACTED in result

    def test_redacts_github_pat(self) -> None:
        pat = "ghp_aBcDeFgHiJkLmNoPqRsTuVwXyZ0123456789"
        result = _redact_patterns(pat)
        assert pat not in result
        assert REDACTED in result

    def test_redacts_long_hex_string(self) -> None:
        hex_key = "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4"
        text = f"API key found: {hex_key}"
        result = _redact_patterns(text)
        assert hex_key not in result

    def test_redacts_ssh_private_key(self) -> None:
        key = "-----BEGIN RSA PRIVATE KEY-----\nMIIE...base64...\n-----END RSA PRIVATE KEY-----"
        result = _redact_patterns(key)
        assert "BEGIN RSA PRIVATE KEY" not in result
        assert REDACTED in result

    def test_preserves_safe_strings(self) -> None:
        safe = "File src/models.py has 3 code smells in class UserService"
        assert _redact_patterns(safe) == safe

    def test_preserves_file_paths(self) -> None:
        path = "src/report/pipeline.py"
        assert _redact_patterns(path) == path

    def test_preserves_short_hex_ids(self) -> None:
        text = "commit abc123"
        assert _redact_patterns(text) == text

    def test_preserves_code_descriptions(self) -> None:
        desc = "Method has cyclomatic complexity of 15, consider refactoring"
        assert _redact_patterns(desc) == desc


# ---------------------------------------------------------------------------
# Recursive sanitization
# ---------------------------------------------------------------------------


class TestSanitizeValue:
    """Tests for sanitize_value recursive walker."""

    def test_redacts_sensitive_dict_key(self) -> None:
        data = {"name": "config.yml", "password": "hunter2"}
        result = sanitize_value(data)
        assert result["name"] == "config.yml"
        assert result["password"] == REDACTED

    def test_recurses_into_nested_dicts(self) -> None:
        data = {"config": {"database": {"db_password": "s3cret"}}}
        result = sanitize_value(data)
        assert result["config"]["database"]["db_password"] == REDACTED

    def test_recurses_into_lists(self) -> None:
        data = [
            {"file": "a.py", "api_key": "key123"},
            {"file": "b.py", "issue": "unused import"},
        ]
        result = sanitize_value(data)
        assert result[0]["api_key"] == REDACTED
        assert result[0]["file"] == "a.py"
        assert result[1]["issue"] == "unused import"

    def test_recurses_into_tuples(self) -> None:
        data = ({"secret": "val"},)
        result = sanitize_value(data)
        assert isinstance(result, tuple)
        assert result[0]["secret"] == REDACTED

    def test_redacts_inline_secret_in_string_value(self) -> None:
        data = {"description": "Connection string: postgresql://user:pass123@host/db"}
        result = sanitize_value(data)
        assert "pass123" not in result["description"]

    def test_passes_through_numbers(self) -> None:
        assert sanitize_value(42) == 42
        assert sanitize_value(3.14) == 3.14

    def test_passes_through_booleans(self) -> None:
        assert sanitize_value(True) is True
        assert sanitize_value(False) is False

    def test_passes_through_none(self) -> None:
        assert sanitize_value(None) is None

    def test_does_not_mutate_input(self) -> None:
        original = {"config": {"password": "secret123", "host": "localhost"}}
        frozen = copy.deepcopy(original)
        sanitize_value(original)
        assert original == frozen


# ---------------------------------------------------------------------------
# Top-level sanitize_agent_results
# ---------------------------------------------------------------------------


class TestSanitizeAgentResults:
    """Tests for the pipeline entry point sanitize_agent_results."""

    def test_sanitizes_across_multiple_agents(self) -> None:
        agent_results = {
            "security_assessor": {
                "overall_score": 75,
                "summary": "Found password=admin123 in config",
                "recommendations": [
                    {
                        "priority": 1,
                        "title": "Remove hardcoded secrets",
                        "description": "File .env contains api_key=sk_live_abc123",
                        "effort": "low",
                    }
                ],
            },
            "code_smell_detector": {
                "grade": "B",
                "total_issues": 5,
                "top_issues": [
                    {
                        "file": "config.py",
                        "issue": "Hardcoded credential: password='hunter2'",
                        "severity": "high",
                        "category": "security",
                    }
                ],
            },
        }
        result = sanitize_agent_results(agent_results)

        # Scores and metadata preserved
        assert result["security_assessor"]["overall_score"] == 75
        assert result["code_smell_detector"]["grade"] == "B"
        assert result["code_smell_detector"]["total_issues"] == 5

        # Sensitive values redacted from strings
        assert "admin123" not in result["security_assessor"]["summary"]
        assert "sk_live_abc123" not in (
            result["security_assessor"]["recommendations"][0]["description"]
        )
        assert "hunter2" not in (
            result["code_smell_detector"]["top_issues"][0]["issue"]
        )

    def test_does_not_mutate_input(self) -> None:
        original = {
            "agent_a": {"password": "secret", "score": 80},
        }
        frozen = copy.deepcopy(original)
        sanitize_agent_results(original)
        assert original == frozen

    def test_preserves_clean_data(self) -> None:
        agent_results = {
            "code_smell_detector": {
                "grade": "A",
                "total_issues": 0,
                "top_issues": [],
            },
        }
        result = sanitize_agent_results(agent_results)
        assert result == agent_results

    def test_handles_empty_results(self) -> None:
        assert sanitize_agent_results({}) == {}

    def test_redacts_sensitive_key_in_generic_agent_extra_fields(self) -> None:
        agent_results = {
            "security_assessor": {
                "overall_score": 60,
                "credentials": {"username": "admin", "password": "p@ss"},
            },
        }
        result = sanitize_agent_results(agent_results)
        assert result["security_assessor"]["credentials"] == REDACTED
        assert result["security_assessor"]["overall_score"] == 60
