import random


class Account:

  def __init__(
      self,
      owner,
      password,
      account_id=None,
      balance=0.0,
      session_limit=10000.0,
      transactions=None,
      notifications=None,
  ):
    self.owner = owner.strip().upper()
    self.password = password

    if account_id is None or account_id == "":
      self.account_id = str(random.randint(100000, 999999))
    else:
      self.account_id = str(account_id)

    self.balance = float(balance)
    self.session_limit = float(session_limit)
    self.session_spent = 0.0

    if transactions is None:
      self.transactions = []
    else:
      self.transactions = transactions

    if notifications is None:
      self.notifications = []
    else:
      self.notifications = notifications

  def check_password(self, input_password):
    return self.password == input_password

  def remaining_session_limit(self):
    remaining = self.session_limit - self.session_spent
    if remaining < 0.0:
      return 0.0
    return remaining

  def add_notification(self, message):
    self.notifications.append(message)

  def clear_notifications(self):
    self.notifications = []

  def to_dict(self):
    return {
        "owner": self.owner,
        "password": self.password,
        "account_id": self.account_id,
        "balance": self.balance,
        "session_limit": self.session_limit,
        "transactions": self.transactions,
        "notifications": self.notifications,
    }


def create_account_from_dict(data):
  owner = data.get("owner", "")
  password = data.get("password", "")
  account_id = data.get("account_id", "")
  balance = data.get("balance", 0.0)
  session_limit = data.get("session_limit", 10000.0)
  transactions = data.get("transactions", [])
  notifications = data.get("notifications", [])

  return Account(
      owner, password, account_id, balance, session_limit, transactions, notifications
  )