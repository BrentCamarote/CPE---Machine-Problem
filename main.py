import ui


def main():
  while True:
    print("====================================")
    print("    EXPENSE TRACKER - MAIN MENU     ")
    print("====================================")
    print("1. Log In")
    print("2. Sign Up (Create New Account)")
    print("3. Exit Program")
    choice = input("Select an option (1-3): ").strip()

    if choice == "1":
      ui.log_in()
    elif choice == "2":
      ui.sign_up()
    elif choice == "3":
      print("\nGoodbye!")
      break
    else:
      print("Invalid selection. Enter 1, 2, or 3.\n")


if __name__ == "__main__":
  main()