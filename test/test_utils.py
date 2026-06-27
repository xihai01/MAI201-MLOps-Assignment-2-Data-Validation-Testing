
"""
Unit tests for data_utils.py

Functions under test:
  - load_csv(filepath)
  - clean_phone(phone)
  - validate_email(email)

Run with:
  pytest test_utils.py -v
"""

import textwrap

import pandas as pd
import pytest

from data_utils import clean_phone, load_csv, validate_email


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def valid_csv(tmp_path):
    """A well-formed CSV with three rows of customer data."""
    path = tmp_path / "customers.csv"
    path.write_text(
        textwrap.dedent("""\
            customer_id,name,age
            C001,Alice,30
            C002,Bob,25
            C003,Carol,40
        """)
    )
    return str(path)


@pytest.fixture
def empty_csv(tmp_path):
    """A CSV file that contains only a header row — no data rows."""
    path = tmp_path / "empty.csv"
    path.write_text("customer_id,name,age\n")
    return str(path)


# ─────────────────────────────────────────────────────────────────────────────
# load_csv
# ─────────────────────────────────────────────────────────────────────────────

class TestLoadCsv:
    """Tests for load_csv(filepath)."""

    # ── Success ───────────────────────────────────────────────────────────────

    def test_returns_dataframe(self, valid_csv):
        """Should return a pandas DataFrame for a valid CSV."""
        result = load_csv(valid_csv)
        assert isinstance(result, pd.DataFrame)

    def test_correct_row_count(self, valid_csv):
        """DataFrame should have the same number of rows as data lines in the file."""
        result = load_csv(valid_csv)
        assert len(result) == 3

    def test_correct_columns(self, valid_csv):
        """DataFrame columns should match the CSV header exactly."""
        result = load_csv(valid_csv)
        assert list(result.columns) == ["customer_id", "name", "age"]

    def test_correct_values(self, valid_csv):
        """First row values should round-trip correctly from the CSV."""
        result = load_csv(valid_csv)
        assert result.iloc[0]["customer_id"] == "C001"
        assert result.iloc[0]["name"] == "Alice"
        assert result.iloc[0]["age"] == 30

    # ── File not found ────────────────────────────────────────────────────────

    def test_raises_file_not_found(self):
        """Should raise FileNotFoundError for a non-existent path."""
        with pytest.raises(FileNotFoundError):
            load_csv("/nonexistent/path/data.csv")

    def test_file_not_found_message_contains_path(self):
        """Error message should include the bad path for easy debugging."""
        bad_path = "/no/such/file.csv"
        with pytest.raises(FileNotFoundError, match=bad_path):
            load_csv(bad_path)

    # ── Empty file ────────────────────────────────────────────────────────────

    def test_raises_value_error_on_empty_file(self, empty_csv):
        """Should raise ValueError when the CSV has a header but no data rows."""
        with pytest.raises(ValueError):
            load_csv(empty_csv)

    def test_empty_file_error_message(self, empty_csv):
        """ValueError message should mention the file path."""
        with pytest.raises(ValueError, match=empty_csv):
            load_csv(empty_csv)


# ─────────────────────────────────────────────────────────────────────────────
# clean_phone
# ─────────────────────────────────────────────────────────────────────────────

class TestCleanPhone:
    """Tests for clean_phone(phone)."""

    # ── Successful normalisation ──────────────────────────────────────────────

    def test_plain_digits(self):
        """10 bare digits should be prefixed with +1."""
        assert clean_phone("4155552671") == "+14155552671"

    def test_dashes(self):
        """Dashes between digit groups should be stripped."""
        assert clean_phone("415-555-2671") == "+14155552671"

    def test_dots(self):
        """Dots as separators should be stripped."""
        assert clean_phone("415.555.2671") == "+14155552671"

    def test_parentheses_and_space(self):
        """Parentheses and spaces (common US format) should be stripped."""
        assert clean_phone("(415) 555-2671") == "+14155552671"

    def test_country_code_1(self):
        """11-digit number starting with 1 should drop the leading 1."""
        assert clean_phone("14155552671") == "+14155552671"

    def test_country_code_with_plus(self):
        """E.164 format with +1 prefix should normalise correctly."""
        assert clean_phone("+14155552671") == "+14155552671"

    def test_mixed_separators(self):
        """Mixed dots, dashes, and spaces should all be stripped."""
        assert clean_phone("1-415.555 2671") == "+14155552671"

    def test_output_format(self):
        """Output must always start with +1 followed by exactly 10 digits."""
        result = clean_phone("800-555-0199")
        assert result.startswith("+1")
        assert len(result) == 12          # +1 + 10 digits
        assert result[2:].isdigit()

    def test_idempotent(self):
        """Calling clean_phone on already-cleaned output should return the same value."""
        cleaned = clean_phone("415-555-2671")
        assert clean_phone(cleaned) == cleaned

    # ── Invalid inputs ────────────────────────────────────────────────────────

    def test_too_few_digits_raises(self):
        """Fewer than 10 digits should raise ValueError."""
        with pytest.raises(ValueError):
            clean_phone("415-555")

    def test_too_many_digits_raises(self):
        """More than 11 digits (or 11 not starting with 1) should raise ValueError."""
        with pytest.raises(ValueError):
            clean_phone("99999999999")

    def test_empty_string_raises(self):
        """An empty string contains no digits and should raise ValueError."""
        with pytest.raises(ValueError):
            clean_phone("")

    def test_letters_only_raises(self):
        """A string with no digits at all should raise ValueError."""
        with pytest.raises(ValueError):
            clean_phone("call me maybe")

    def test_non_string_raises(self):
        """Passing a non-string (e.g. int) should raise ValueError."""
        with pytest.raises(ValueError):
            clean_phone(4155552671)

    def test_none_raises(self):
        """None should raise ValueError."""
        with pytest.raises(ValueError):
            clean_phone(None)

    def test_error_message_contains_input(self):
        """ValueError message should include the offending input."""
        bad = "123-abc"
        with pytest.raises(ValueError, match="123-abc"):
            clean_phone(bad)

    def test_negative_number_string_raises(self):
        """A negative number string like '-8437' has only 4 digits — should fail."""
        with pytest.raises(ValueError):
            clean_phone("-8437")


# ─────────────────────────────────────────────────────────────────────────────
# validate_email
# ─────────────────────────────────────────────────────────────────────────────

class TestValidateEmail:
    """Tests for validate_email(email)."""

    # ── Valid emails ──────────────────────────────────────────────────────────

    def test_simple_valid(self):
        assert validate_email("user@example.com") is True

    def test_subdomain(self):
        assert validate_email("user@mail.example.com") is True

    def test_plus_addressing(self):
        """Plus-sign tags (e.g. Gmail filters) are valid."""
        assert validate_email("user+tag@example.com") is True

    def test_dots_in_local(self):
        """Dots in the local part are allowed."""
        assert validate_email("first.last@example.com") is True

    def test_numeric_local(self):
        """All-numeric local part is valid."""
        assert validate_email("12345@example.com") is True

    def test_short_tld(self):
        """Two-character TLDs (country codes) are valid."""
        assert validate_email("user@example.ca") is True

    def test_long_tld(self):
        """TLDs up to 6 characters are valid (e.g. .museum)."""
        assert validate_email("user@example.museum") is True

    def test_hyphen_in_domain(self):
        """Hyphens in the domain name are valid."""
        assert validate_email("user@my-company.com") is True

    def test_underscore_in_local(self):
        """Underscores in the local part are valid."""
        assert validate_email("user_name@example.com") is True

    def test_leading_trailing_spaces_stripped(self):
        """Surrounding whitespace should be stripped before validation."""
        assert validate_email("  user@example.com  ") is True

    # ── Invalid emails ────────────────────────────────────────────────────────

    def test_missing_at_sign(self):
        assert validate_email("userexample.com") is False

    def test_missing_local_part(self):
        """@ with nothing before it is invalid."""
        assert validate_email("@domain.com") is False

    def test_missing_domain(self):
        """Nothing after @ is invalid."""
        assert validate_email("user@") is False

    def test_missing_tld(self):
        """Domain without a dot (no TLD) is invalid."""
        assert validate_email("user@domain") is False

    def test_double_at_sign(self):
        assert validate_email("user@@example.com") is False

    def test_spaces_in_address(self):
        """Internal spaces are not valid in an email address."""
        assert validate_email("user name@example.com") is False

    def test_empty_string(self):
        assert validate_email("") is False

    def test_only_at_sign(self):
        assert validate_email("@") is False

    # ── Edge cases ────────────────────────────────────────────────────────────

    def test_none_returns_false(self):
        """None is not a string — should return False, not raise."""
        assert validate_email(None) is False

    def test_integer_returns_false(self):
        """Non-string types should return False gracefully."""
        assert validate_email(12345) is False

    def test_tld_too_long(self):
        """TLD longer than 6 characters is outside the accepted range."""
        assert validate_email("user@example.toolongtld") is False

    def test_dot_at_start_of_local(self):
        """Leading dot in local part is technically invalid per RFC 5321."""
        assert validate_email(".user@example.com") is False

    def test_consecutive_dots_in_local(self):
        """Consecutive dots in local part are invalid per RFC 5321."""
        assert validate_email("user..name@example.com") is False
