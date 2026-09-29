import json
import os


def save_account_data(account_data):
  """Saves or updates account JSON using the permanent account_id in the filename."""
  account_id = account_data["account_id"]
  filename = "expenses_" + str(account_id) + ".json"

  try:
    file = open(filename, "w")
    json.dump(account_data, file, indent=4)
    file.close()
    return True
  except:
    return False


def find_account_data(identifier):
  """Searches directory JSON files for a match against Account ID or Owner Name (case-insensitive)."""
  target = identifier.strip().upper()

  for filename in os.listdir("."):
    if filename.startswith("expenses_") and filename.endswith(".json"):
      try:
        file = open(filename, "r")
        data = json.load(file)
        file.close()

        stored_id = str(data.get("account_id", ""))
        stored_owner = str(data.get("owner", "")).upper()

        if stored_id == target or stored_owner == target:
          return data
      except:
        continue

  return None


def account_exists(identifier):
  found_data = find_account_data(identifier)
  if found_data is not None:
    return True
  else:
    return False