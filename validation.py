"""validation.py - Pure operational validation and input sanitization module."""


def parse_amount(input_str):
  clean_str = input_str.strip().replace("$", "").replace(",", "")

  try:
    amount = float(clean_str)
    if amount <= 0:
      return None, "Amount must be greater than $0.00."

    return round(amount, 2), None
  except ValueError:
    return None, "Invalid input. Please enter a valid number (e.g., 67.09)."


def validate_withdrawal_or_transfer(account, amount):
  remaining_limit = account.remaining_session_limit()

  if amount > remaining_limit:
    msg = (
        "Exceeds session limit! Max remaining allowed: $"
        + f"{remaining_limit:.2f}"
    )
    return False, msg, "LIMIT_EXCEEDED"

  if amount > account.balance:
    msg = f"Insufficient funds! Current balance: ${account.balance:.2f}"
    return False, msg, "INSUFFICIENT_FUNDS"

  return True, None, "SUCCESS"


def validate_bill_amount(account, amount):
  if amount > account.balance:
    msg = f"Insufficient funds! Current balance: ${account.balance:.2f}"
    return False, msg, "INSUFFICIENT_FUNDS"
  return True, None, "SUCCESS"


def validate_text_input(input_str, field_name):
  cleaned = input_str.strip()
  if cleaned == "":
    return None, field_name + " cannot be empty."
  return cleaned, None