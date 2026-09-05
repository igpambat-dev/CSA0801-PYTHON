import mysql.connector

# Connect to MySQL
db = mysql.connector.connect(
    host="127.0.0.1",
    port=3306,
    user="root",
    password="310309",
    database="bank_management"
)

cursor = db.cursor()


def create_account():
    try:
        account_no = int(input("Enter Account Number: "))
        name = input("Enter Name: ")
        phone = input("Enter Phone Number: ")
        account_type = input("Enter Account Type (Savings/Current): ")
        pin = int(input("Enter PIN: "))
        balance = float(input("Enter Initial Balance: "))

        query = """
        INSERT INTO accounts
        (account_no, name, phone, account_type, pin, balance)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        values = (account_no, name, phone, account_type, pin, balance)

        cursor.execute(query, values)
        db.commit()

        print("Account created successfully!")

    except mysql.connector.Error as e:
        print("Error:", e)


def view_accounts():
    cursor.execute("SELECT * FROM accounts")
    records = cursor.fetchall()

    print("\n----- ACCOUNT DETAILS -----")

    if len(records) == 0:
        print("No accounts found.")
    else:
        for row in records:
            print("Account No :", row[0])
            print("Name       :", row[1])
            print("Phone      :", row[2])
            print("Type       :", row[3])
            print("Balance    :", row[5])
            print("---------------------------")


def deposit():
    try:
        account_no = int(input("Enter Account Number: "))
        amount = float(input("Enter Deposit Amount: "))

        if amount <= 0:
            print("Invalid amount.")
            return

        cursor.execute(
            "SELECT balance FROM accounts WHERE account_no = %s",
            (account_no,)
        )

        result = cursor.fetchone()

        if result is None:
            print("Account not found.")
            return

        new_balance = float(result[0]) + amount

        cursor.execute(
            "UPDATE accounts SET balance = %s WHERE account_no = %s",
            (new_balance, account_no)
        )

        cursor.execute(
            """
            INSERT INTO transactions
            (account_no, transaction_type, amount)
            VALUES (%s, %s, %s)
            """,
            (account_no, "Deposit", amount)
        )

        db.commit()

        print("Amount deposited successfully!")
        print("New Balance:", new_balance)

    except mysql.connector.Error as e:
        print("Error:", e)


def withdraw():
    try:
        account_no = int(input("Enter Account Number: "))
        amount = float(input("Enter Withdrawal Amount: "))

        if amount <= 0:
            print("Invalid amount.")
            return

        cursor.execute(
            "SELECT balance FROM accounts WHERE account_no = %s",
            (account_no,)
        )

        result = cursor.fetchone()

        if result is None:
            print("Account not found.")
            return

        balance = float(result[0])

        if amount > balance:
            print("Insufficient balance.")
            return

        new_balance = balance - amount

        cursor.execute(
            "UPDATE accounts SET balance = %s WHERE account_no = %s",
            (new_balance, account_no)
        )

        cursor.execute(
            """
            INSERT INTO transactions
            (account_no, transaction_type, amount)
            VALUES (%s, %s, %s)
            """,
            (account_no, "Withdrawal", amount)
        )

        db.commit()

        print("Amount withdrawn successfully!")
        print("New Balance:", new_balance)

    except mysql.connector.Error as e:
        print("Error:", e)


def view_transactions():
    try:
        account_no = int(input("Enter Account Number: "))

        cursor.execute(
            """
            SELECT transaction_id, transaction_type, amount, transaction_date
            FROM transactions
            WHERE account_no = %s
            ORDER BY transaction_date DESC
            """,
            (account_no,)
        )

        records = cursor.fetchall()

        print("\n----- TRANSACTION HISTORY -----")

        if len(records) == 0:
            print("No transactions found.")
        else:
            for row in records:
                print("Transaction ID :", row[0])
                print("Type           :", row[1])
                print("Amount         :", row[2])
                print("Date           :", row[3])
                print("-------------------------------")

    except mysql.connector.Error as e:
        print("Error:", e)


def check_balance():
    try:
        account_no = int(input("Enter Account Number: "))

        cursor.execute(
            "SELECT name, balance FROM accounts WHERE account_no = %s",
            (account_no,)
        )

        result = cursor.fetchone()

        if result is None:
            print("Account not found.")
        else:
            print("Account Holder:", result[0])
            print("Current Balance:", result[1])

    except mysql.connector.Error as e:
        print("Error:", e)


# Main Menu
while True:

    print("\n================================")
    print("      BANK MANAGEMENT SYSTEM")
    print("================================")
    print("1. Create Account")
    print("2. View All Accounts")
    print("3. Deposit Money")
    print("4. Withdraw Money")
    print("5. Check Balance")
    print("6. View Transactions")
    print("7. Exit")
    print("================================")

    choice = input("Enter your choice: ")

    if choice == "1":
        create_account()

    elif choice == "2":
        view_accounts()

    elif choice == "3":
        deposit()

    elif choice == "4":
        withdraw()

    elif choice == "5":
        check_balance()

    elif choice == "6":
        view_transactions()

    elif choice == "7":
        print("Thank you for using Bank Management System!")
        break

    else:
        print("Invalid choice. Please try again.")


cursor.close()
db.close()
