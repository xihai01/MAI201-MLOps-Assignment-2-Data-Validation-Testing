import pandas as pd
import re

def load_csv(filepath: str) -> pd.DataFrame:
    """Load a CSV file and return a DataFrame.

    Raises:
        FileNotFoundError: if the file does not exist.
        ValueError: if the file is empty or has no data rows.
    """
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {filepath}")

    if df.empty:
        raise ValueError(f"File is empty or contains no data rows: {filepath}")

    return df


def clean_phone(phone: str) -> str:
    """Normalise a phone number to the format +1XXXXXXXXXX.

    Strips all non-digit characters, validates length (10 digits for North
    American numbers, or 11 digits starting with 1), and returns a
    standardised string.

    Raises:
        ValueError: if the input cannot be converted to a valid 10-digit
                    North American phone number.
    """
    if not isinstance(phone, str):
        raise ValueError(f"Expected a string, got {type(phone).__name__}")

    digits = re.sub(r"\D", "", phone)

    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]

    if len(digits) != 10:
        raise ValueError(
            f"Invalid phone number '{phone}': expected 10 digits, got {len(digits)}"
        )

    return f"+1{digits}"


def validate_email(email: str) -> bool:
    """Return True if *email* matches a broadly valid email pattern.

    Checks for:
      - one or more characters before the @
      - a domain with at least one dot
      - a TLD of 2–6 characters
    """
    if not isinstance(email, str):
        return False

    # Local part: must start and end with an alphanumeric or special char
    # (not a dot), and must not contain consecutive dots.
    pattern = r"^[a-zA-Z0-9_%+\-]+([.][a-zA-Z0-9_%+\-]+)*@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,6}$"
    return bool(re.match(pattern, email.strip()))
