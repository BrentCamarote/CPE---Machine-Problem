import storage
import validation

BILL_CATEGORIES = {
    "1": "Electricity",
    "2": "Water",
    "3": "Rent",
    "4": "Groceries",
    "5": "Credit Card",
    "6": "Internet/Cable",
    "7": "Mobile/Postpaid",
    "8": "Tuition/Education",
    "9": "Miscellaneous",
}


def process_deposit(account, amount):
  account.balance += amount
  record = {
      "amount": amount,
      "type": "deposit",
      "category": "Deposit",
      "description": "Quick Deposit",
  }
  account.transactions.append(record)
  save_success = storage.save_account_data(account.to_dict())

  if save_success:
    return True, f"Success! ${amount:.2f} deposited."
  else:
    return False, "Failed to update storage file."


def process_withdrawal(account, amount):
  is_valid, error_msg, reason = validation.validate_withdrawal_or_transfer(
      account, amount
  )
  if not is_valid:
    return False, error_msg, reason

  account.balance -= amount
  account.session_spent += amount

  record = {
      "amount": amount,
      "type": "withdrawal",
      "category": "Withdrawal",
      "description": "Cash Withdrawal",
  }
  account.transactions.append(record)
  storage.save_account_data(account.to_dict())

  return True, f"Successfully withdrew ${amount:.2f}!", "SUCCESS"


def process_transfer(account, target_identifier, amount, auth_password):
  recipient_data = storage.find_account_data(target_identifier)
  if recipient_data is None:
    return False, "No account exists with such name or ID.", "NOT_FOUND"

  if recipient_data["account_id"] == account.account_id:
    return False, "You cannot transfer funds to your own account!", "SELF_TRANSFER"

  is_valid, error_msg, reason = validation.validate_withdrawal_or_transfer(
      account, amount
  )
  if not is_valid:
    return False, error_msg, reason

  if not account.check_password(auth_password):
    return (
        False,
        "Authentication failed! Incorrect password. Transfer aborted.",
        "AUTH_FAILED",
    )

  account.balance -= amount
  account.session_spent += amount

  sender_record = {
      "amount": amount,
      "type": "transfer_send",
      "recipient": recipient_data["owner"],
      "description": f"Transfer to {recipient_data['owner']}",
  }
  account.transactions.append(sender_record)
  storage.save_account_data(account.to_dict())

  recipient_data["balance"] += amount
  recipient_record = {
      "amount": amount,
      "type": "transfer_receive",
      "sender": account.owner,
      "description": f"Transfer from {account.owner}",
  }
  recipient_data["transactions"].append(recipient_record)

  if "notifications" not in recipient_data:
    recipient_data["notifications"] = []
  recipient_data["notifications"].append(
      f"{account.owner} sent you ${amount:.2f}"
  )

  storage.save_account_data(recipient_data)

  msg = f"Success! Transferred ${amount:.2f} to {recipient_data['owner']}."
  return True, msg, "SUCCESS"


def process_bill_payment(account, category_key, amount):
  if category_key not in BILL_CATEGORIES:
    return False, "Invalid bill category selection.", "INVALID_CATEGORY"

  selected_category = BILL_CATEGORIES[category_key]

  is_valid, error_msg, reason = validation.validate_bill_amount(
      account, amount
  )
  if not is_valid:
    return False, error_msg, reason

  account.balance -= amount
  record = {
      "amount": amount,
      "type": "bill",
      "category": selected_category,
      "description": f"Bills_{selected_category}",
  }
  account.transactions.append(record)
  storage.save_account_data(account.to_dict())

  msg = f"Paid ${amount:.2f} for {selected_category} Bill."
  return True, msg, "SUCCESS"


def process_adjust_limit(account, new_limit):
  if new_limit < account.session_spent:
    return False, "New limit cannot be less than what you have already spent!"
  elif new_limit > 250000:
    return False, "Maximum allowed spending limit is $250,000.00."
  else:
    account.session_limit = new_limit
    storage.save_account_data(account.to_dict())
    return True, f"Session limit updated to ${account.session_limit:.2f}!"