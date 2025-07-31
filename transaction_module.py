from firebase_admin import firestore
from budget_module import Budget
from asset_module import AssetManager
from datetime import datetime, date
from collections import defaultdict

# turns string into date
def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None

#ensures date string fits required parameters
def validate_date(input_str):
    try:
        datetime.strptime(input_str, "%Y-%m-%d")
        return input_str
    except ValueError:
        print("Invalid date format. Use YYYY-MM-DD.")
        return None

class TransactionManager:
    def __init__(self, userId):
        self.userId = userId
        self.budget = Budget(userId)
        self.asset_manager = AssetManager(userId)
        self.db = firestore.client()
        self.categoryKeys = [
            "housing", "insurance", "food", "savings", "transport",
            "giving", "personal", "recreation", "utilities", "medical", "clothing", "income"
        ]
        self.refreshTransactions()

        if not self.transactions:
            print("No transactions have been entered")

    # ensures program is accessing most current firestore data
    def refreshTransactions(self):
        query = self.db.collection("transactions").where("userId", "==", self.userId)
        self.transactions = list(query.stream())

    #allows user to choose category from a list
    def chooseCategory(self):
        print("\nChoose a category:")
        for i, key in enumerate(self.categoryKeys, start=1):
            print(f"{i}. {key.capitalize()}")
        print("0. Quit")

        try:
            category = int(input("Enter category number: "))
            if category == 0:
                return None
            elif 1 <= category <= len(self.categoryKeys):
                return self.categoryKeys[category - 1]
            else:
                print("Invalid choice.")
                return None
        except ValueError:
            print("Please enter a valid number.")
            return None

    #add transaction to firestore
    def addTransaction(self):
        print("\n📌 Enter New Transaction")

        while True:
            try:
                amount = float(input("Amount: $"))
                if amount <= 0:
                    print("Amount must be greater than 0.")
                    continue
                break
            except ValueError:
                print("Please enter a valid number.")

        category = self.chooseCategory()
        if category is None:
            print("Transaction cancelled.")
            return

        while True:
            date_input = input("Date of Transaction (YYYY-MM-DD): ")
            date = validate_date(date_input)
            if date:
                break

        description = input("Description of Transaction (e.g., Weekly Groceries): ")

        transactionData = {
            "amount": amount,
            "category": category,
            "date": date,
            "description": description,
            "userId": self.userId
        }
        self.asset_manager.updateByTransaction(amount, category)
        self.db.collection("transactions").document().create(transactionData)
        print(f"✅ Added {category.capitalize()} transaction of ${amount:.2f} on {date}.")
        self.refreshTransactions()

    #allows the user to choose whether to edit or delete transaction
    def editTransactionMenu(self):
        while True:
            transaction = self.chooseTransaction()
            if transaction is None:
                break

            option = input("1. Edit Transaction\n2. Delete Transaction\n3. Quit\nEnter choice: ")
            if option == "1":
                self.editTransaction(transaction)
            elif option == "2":
                self.deleteTransaction(transaction)
            elif option == "3":
                break
            else:
                print("Invalid option.")

    #delete transaction from firestore
    def deleteTransaction(self, transaction):
        print("\n🗑️ Delete Transaction")
        print("⚠️ Once deleted, this cannot be undone.")
        print(f"Amount: {transaction['amount']}\nCategory: {transaction['category']}\nDate: {transaction['date']}\nDescription: {transaction['description']}")
        deleteInput = input("Do you wish to continue deleting this transaction? (y/n): ").strip().lower()
        if deleteInput == "y":
            self.db.collection("transactions").document(transaction['docId']).delete()
            print("✅ Transaction deleted.")
            self.refreshTransactions()

    #updates transaction in firestore
    def editTransaction(self, transaction):
        print("\n✏️ Edit Transaction")

        # Amount
        while True:
            try:
                amount = float(input(f"Current Amount = ${transaction['amount']} | New Amount: $"))
                if amount <= 0:
                    print("Amount must be greater than 0.")
                    continue
                break
            except ValueError:
                print("Please enter a valid number.")

        # Category
        category = self.chooseCategory()
        if category is None:
            print("Transaction cancelled.")
            return

        # Date
        while True:
            date_input = input(f"Current Date: {transaction['date']} | New Date (YYYY-MM-DD): ")
            date = validate_date(date_input)
            if date:
                break

        # Description
        description = input(f"Current Description: {transaction['description']} | New Description: ")

        # Prepare updated data
        transactionData = {
            "amount": amount,
            "category": category,
            "date": date,
            "description": description,
            "userId": self.userId,
            "docId": transaction["docId"]
        }

        # Reverse old transaction
        reverse_category = "income" if transaction["category"] != "income" else "expense"
        self.asset_manager.updateByTransaction(transaction["amount"], reverse_category)

        # Apply new transaction
        self.asset_manager.updateByTransaction(amount, category)

        # Update Firestore
        self.db.collection("transactions").document(transaction['docId']).set(transactionData)
        print(f"✅ Updated {category.capitalize()} transaction of ${amount:.2f} on {date}.")
        self.refreshTransactions()

    #allows user to choose transaction from list
    def chooseTransaction(self):
        if not self.transactions:
            print("No transactions available.")
            return None

        print("\n📋 Choose a Transaction:")
        for i, doc in enumerate(self.transactions, start=1):
            tx = doc.to_dict()
            print(f"{i}. Amount: ${tx['amount']:.2f} | Category: {tx['category']} | Date: {tx['date']} | Description: {tx['description']}")
        print("0. Quit")

        try:
            chosen = int(input("Enter transaction number: "))
            if chosen == 0:
                return None
            elif 1 <= chosen <= len(self.transactions):
                doc = self.transactions[chosen - 1]
                tx = doc.to_dict()
                tx['docId'] = doc.id
                return tx
            else:
                print("Invalid choice.")
                return None
        except ValueError:
            print("Please enter a valid number.")
            return None

    #creates a list of transactions
    def listTransactions(self):
        if not self.transactions:
            print("No transactions to display.")
            return

        print("\n📋 All Transactions:")
        for doc in self.transactions:
            tx = doc.to_dict()
            print(f"- ${tx['amount']:.2f} | {tx['category']} | {tx['date']} | {tx['description']}")

    #summarizes transactions based on time period
    def summarizeTransactions(self, period="weekly"):
        today = date.today()
        summary = defaultdict(float)

        for doc in self.transactions:
            tx = doc.to_dict()
            tx_date = parse_date(tx.get("date"))
            if not tx_date:
                continue

            if period == "weekly" and (today - tx_date).days <= 7:
                summary[tx["category"]] += tx["amount"]
            elif period == "monthly" and tx_date.month == today.month and tx_date.year == today.year:
                summary[tx["category"]] += tx["amount"]
            elif period == "annual" and tx_date.year == today.year:
                summary[tx["category"]] += tx["amount"]

        print(f"\n📈 {period.capitalize()} Summary:")
        if not summary:
            print("No transactions found for this period.")
            return

        for category, total in summary.items():
            print(f"{category.capitalize()}: ${total:.2f}")

        summaryInput = input("Do you wish to compare your budget? y/n ").strip().lower()
        if summaryInput == "y":
            self.compareBudget(summary, period)

    #allows user to compare current spending to budget
    def compareBudget(self, summary, period):
        print(f"\n📊 Comparing {period} spending to your budget:")
        for category, spent in summary.items():
            budgeted = self.budget.getCategoryBudget(category, period)
            if budgeted is None:
                print(f"{category.capitalize()}: No budget set.")
                continue

            diff = spent - budgeted
            status = "✅ Under Budget" if diff <= 0 else "⚠️ Over Budget"
            print(f"{category.capitalize()}: Spent ${spent:.2f} / Budget ${budgeted:.2f} → {status}")

    #transaction manager menu
    def transactionMenu(self):
        while True:
            menuInput = input(
                "\n📂 Transaction Menu\n"
                "1. Add Transaction\n"
                "2. Edit/Delete Transactions\n"
                "3. View Weekly Summary\n"
                "4. View Monthly Summary\n"
                "5. View Annual Summary\n"
                "6. View All Transactions\n"
                "7. Return to Main Menu\n"
                "Enter choice: "
            )

            if menuInput == "1":
                self.addTransaction()
            elif menuInput == "2":
                self.editTransactionMenu()
            elif menuInput == "3":
                self.summarizeTransactions("weekly")
            elif menuInput == "4":
                self.summarizeTransactions("monthly")
            elif menuInput == "5":
                self.summarizeTransactions("annual")
            elif menuInput == "6":
                self.listTransactions()
            elif menuInput == "7":
                print("Returning to Main")
                return None