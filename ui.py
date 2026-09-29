from account import Account, create_account_from_dict
import storage
import transactions
import validation


def print_header(title):
  print("\n" + "=" * 45)
  print(f"  {title.upper()}")
  print("=" * 45)


def display_dashboard(account):
  print_header(f"ACCOUNT DASHBOARD | OWNER: {account.owner}")
  print(f" Account ID      : {account.account_id}")
  print(f" Current Balance : ${account.balance:.2f}")
  print(
      f" Session Limit   : ${account.remaining_session_limit():.2f} /"
      f" ${account.session_limit:.2f}"
  )

  # Notifications / Mailbox
  print("-" * 45)
  print(" MAILBOX / NOTIFICATIONS:")
  if len(account.notifications) > 0:
    for note in account.notifications:
      print(f"  [MAIL] {note}")
    account.clear_notifications()
    storage.save_account_data(account.to_dict())
  else:
    print("  No new mail")
  print("=" * 45 + "\n")


def display_transaction_history(account):
  print_header(f"TRANSACTION HISTORY ({account.owner})")

  if not account.transactions:
    print("No recorded transactions found.\n")
    return

  idx = 1
  for tx in account.transactions:
    tx_type = tx.get("type", "")
    amt = tx.get("amount", 0.0)

    if tx_type == "bill":
      cat = tx.get("category", "General")
      print(
          f"#{idx}.) -${amt:.2f} | {account.owner} | Transaction: Bills ({cat})"
      )
    elif tx_type == "deposit":
      print(f"#{idx}.) +${amt:.2f} | {account.owner} | Transaction: Deposit")
    elif tx_type == "withdrawal":
      print(f"#{idx}.) -${amt:.2f} | {account.owner} | Transaction: Withdrawal")
    elif tx_type == "transfer_send":
      recipient = tx.get("recipient", "UNKNOWN")
      print(
          f"#{idx}.) -${amt:.2f} | {account.owner} -> {recipient} |"
          " Transaction: Transfer (Send)"
      )
    elif tx_type == "transfer_receive":
      sender = tx.get("sender", "UNKNOWN")
      print(
          f"#{idx}.) +${amt:.2f} | {sender} -> {account.owner} |"
          " Transaction: Transfer (Receive)"
      )

    idx += 1

  print("====================================\n")


def show_insufficient_funds_menu(account):
  print(f"\n[!] INSUFFICIENT FUNDS! Current Balance: ${account.balance:.2f}")
  print("1. Return to Previous Menu")
  print("2. Quick Deposit")
  print("3. Exit Session (Logout)")

  choice = input("Select an option (1-3): ").strip()
  if choice == "2":
    ui_quick_deposit(account)
  return choice


def ui_quick_deposit(account):
  print_header("QUICK DEPOSIT")
  raw_input = input("Enter deposit amount: $")

  amount, error = validation.parse_amount(raw_input)
  if error is not None:
    print(f"[Error] {error}\n")
    return

  success, msg = transactions.process_deposit(account, amount)
  if success:
    print(f"{msg} New Balance: ${account.balance:.2f}\n")
  else:
    print(f"[Error] {msg}\n")


def ui_withdraw_cash(account):
  print_header("WITHDRAW CASH")
  print(f"Current Balance: ${account.balance:.2f}")
  print(f"Remaining Session Limit: ${account.remaining_session_limit():.2f}")

  raw_input = input("Enter withdrawal amount: $")
  amount, error = validation.parse_amount(raw_input)
  if error is not None:
    print(f"[Error] {error}\n")
    return "1"

  success, msg, reason = transactions.process_withdrawal(account, amount)
  if not success:
    if reason == "INSUFFICIENT_FUNDS":
      return show_insufficient_funds_menu(account)
    else:
      print(f"[Error] {msg}\n")
      return "1"

  print(f"{msg} Remaining Balance: ${account.balance:.2f}\n")
  return "1"


def ui_transfer_funds(account):
  print_header("TRANSFER FUNDS")
  target = input("Enter Recipient Account Name or 6-digit ID: ").strip()

  raw_input = input("Enter transfer amount: $")
  amount, error = validation.parse_amount(raw_input)
  if error is not None:
    print(f"[Error] {error}\n")
    return "1"

  auth_pass = input("Enter YOUR Account Password to authorize: ").strip()

  rec_data = storage.find_account_data(target)
  if rec_data is not None:
    print(
        f"\nConfirm Transfer of ${amount:.2f} to {rec_data['owner']} (ID:"
        f" {rec_data['account_id']})?"
    )
    print("1 = YES | 0 = NO")
    confirm = input("Selection (1/0): ").strip()
    if confirm != "1":
      print("Transfer cancelled.\n")
      return "1"

  success, msg, reason = transactions.process_transfer(
      account, target, amount, auth_pass
  )
  if not success:
    if reason == "INSUFFICIENT_FUNDS":
      return show_insufficient_funds_menu(account)
    else:
      print(f"[Error] {msg}\n")
      return "1"

  print(f"{msg} New Balance: ${account.balance:.2f}\n")
  return "1"


def ui_pay_bills(account):
  print_header("PAY BILLS")
  print("Select Bill Category:")
  for key in transactions.BILL_CATEGORIES:
    print(f" {key}. {transactions.BILL_CATEGORIES[key]} Bill")
  print(" 0. Return to Menu")

  cat_choice = input("Select category (0-9): ").strip()
  if cat_choice == "0":
    return "1"

  if cat_choice not in transactions.BILL_CATEGORIES:
    print("[Error] Invalid category choice.\n")
    return "1"

  cat_name = transactions.BILL_CATEGORIES[cat_choice]
  raw_input = input(f"Enter amount for {cat_name} Bill: $")

  amount, error = validation.parse_amount(raw_input)
  if error is not None:
    print(f"[Error] {error}\n")
    return "1"

  success, msg, reason = transactions.process_bill_payment(
      account, cat_choice, amount
  )
  if not success:
    if reason == "INSUFFICIENT_FUNDS":
      return show_insufficient_funds_menu(account)
    else:
      print(f"[Error] {msg}\n")
      return "1"

  print(f"{msg} New Balance: ${account.balance:.2f}\n")
  return "1"


def ui_adjust_spending_limit(account):
  print(
      f"\nCurrent Session Spending Limit: ${account.session_limit:.2f} (Spent:"
      f" ${account.session_spent:.2f})"
  )
  raw_input = input(
      "Enter new session limit (Default $10,000 | Max $250,000): $"
  )
  new_limit, error = validation.parse_amount(raw_input)

  if error is not None:
    print(f"[Error] {error}\n")
    return

  success, msg = transactions.process_adjust_limit(account, new_limit)
  if success:
    print(f"{msg}\n")
  else:
    print(f"[Error] {msg}\n")


def logged_in_session(account):
  display_dashboard(account)

  while True:
    print("--- MAIN INTERACTION MENU ---")
    print("1. Withdraw Cash")
    print("2. Transfer Income")
    print("3. Pay Bills")
    print("4. Deposit Funds")
    print("5. View Transaction History")
    print("6. Adjust Session Spending Limit")
    print("7. Save & Exit Session (Logout)")

    choice = input("Select an option (1-7): ").strip()

    result = "1"
    if choice == "1":
      result = ui_withdraw_cash(account)
    elif choice == "2":
      result = ui_transfer_funds(account)
    elif choice == "3":
      result = ui_pay_bills(account)
    elif choice == "4":
      ui_quick_deposit(account)
    elif choice == "5":
      display_transaction_history(account)
    elif choice == "6":
      ui_adjust_spending_limit(account)
    elif choice == "7":
      print(f"\nLogged out of {account.owner}. Session closed.\n")
      break
    else:
      print("Invalid choice. Enter 1-7.\n")

    if result == "3":
      print("\nSession exited.\n")
      break


def sign_up():
  print_header("CREATE NEW ACCOUNT")
  print("(Type '0' or 'cancel' to return to Main Menu)")

  raw_name = input("Enter new Account Name: ")
  cleaned_check = raw_name.strip().lower()

  if cleaned_check == "0" or cleaned_check == "cancel":
    print("Sign-up cancelled.\n")
    return

  username, err = validation.validate_text_input(raw_name, "Account Name")
  if err is not None:
    print(f"[Error] {err}\n")
    return

  username = username.upper()

  if storage.account_exists(username):
    print(f"Account '{username}' already exists! Please log in.\n")
    return

  raw_pass = input("Enter Password: ")
  pass_check = raw_pass.strip().lower()

  if pass_check == "0" or pass_check == "cancel":
    print("Sign-up cancelled.\n")
    return

  password, err = validation.validate_text_input(raw_pass, "Password")
  if err is not None:
    print(f"[Error] {err}\n")
    return

  new_account = Account(username, password)
  if storage.save_account_data(new_account.to_dict()):
    print(
        f"\nAccount created successfully! Auto-generated ID:"
        f" {new_account.account_id}"
    )
    logged_in_session(new_account)


def log_in():
  print_header("LOGIN")
  identifier = input("Enter Account Name or 6-digit ID: ").strip()

  raw_data = storage.find_account_data(identifier)
  if raw_data is None:
    print("No account exists with such name or ID.\n")
    return

  password = input("Password: ").strip()
  account = create_account_from_dict(raw_data)

  if not account.check_password(password):
    print("Incorrect password for this account.\n")
    return

  print(f"\nLogin successful! Welcome back, {account.owner}.")
  logged_in_session(account)