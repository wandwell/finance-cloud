from firebase_admin import firestore

class Budget:
    def __init__(self, userId):
        self.userId = userId
        self.db = firestore.client()
        query = self.db.collection("budgets").where("userId", "==", userId).limit(1)
        results = list(query.stream())
        self.isBasicBudget = True

        # Use user-specific budget if found
        if results:
            doc = results[0]
            self.isBasicBudget = False
        else:
            print("User budget not found, using basic budget.")
            doc = self.db.collection("budgets").document("1QGu5BbzPiyv1mqlZmue").get()
            if not doc.exists:
                raise ValueError("Basic budget not found in Firestore.")

        self.budgetDict = doc.to_dict()
        print (self.budgetDict)
        self.budgetId = doc.id
        self.annIncome = self.budgetDict.get("annIncome")

        # Loop to set budget categories
        self.budgetKeys = [
            "housing", "insurance", "food", "saving", "transport",
            "giving", "personal", "recreation", "utilities", "medical", "clothing"
        ]
        for key in self.budgetKeys:
            setattr(self, key, self.budgetDict.get(key))

    #allows user to choose a specific category
    def chooseCategory(self):
        print("\nChoose a category to adjust:")
        for i, key in enumerate(self.budgetKeys, start=1):
            percent = getattr(self, key)  # Use live attribute 1
            amount = (self.annIncome / 52) * (percent / 100)
            print(f"{i}. {key.capitalize()} | {percent:.2f}% | ${amount:.2f}")
        print("0. Quit")

        try:
            category = int(input("Enter category number: "))
            if category == 0:
                return None
            elif 1 <= category <= len(self.budgetKeys):
                return self.budgetKeys[category - 1]
            else:
                print("Invalid choice.")
                return None
        except ValueError:
            print("Please enter a valid number.")
            return None

    #allows user to view current budget - also functions as the menu
    def viewBudget(self):
        weeklyIncome = self.annIncome / 12
        print(f"\nAvg Weekly Income: ${weeklyIncome:.2f}")

        for i, key in enumerate(self.budgetKeys, start=1):
            percent = getattr(self, key)
            amount = weeklyIncome * (percent / 100)
            print(f"{i}. {key.capitalize()} %: {percent} | $ {amount:.2f}")

        budgetMenuInput = input(
            "\n1. Change Budget by Percentage\n2. Change Budget by Amount\n3. Change Annual Income\n4. Return to Main Menu\nEnter your choice: "
        )
        if budgetMenuInput == "1":
            self.changeBudgetPercentage()
        elif budgetMenuInput == "2":
            self.changeBudgetAmounts(weeklyIncome)
        elif budgetMenuInput == "3":
            new_income = int(input("What is the your Annual Income? "))
            self.annIncome = new_income
            self.budgetDict["annIncome"] = new_income
            self.saveBudget()
            self.viewBudget()
        else: 
            return

    #change budget based on the percentages
    def changeBudgetPercentage(self):
        print("\n🔧 Update multiple budget categories. Enter 0 to finish.")
        while True:
            key = self.chooseCategory()
            if not key:
                break

            try:
                new_percent = float(input(f"Enter new percentage for {key}: "))
                setattr(self, key, new_percent)
                print(f"✅ {key.capitalize()} updated to {new_percent}%.")
                total = sum(getattr(self, key) for key in self.budgetKeys)
                print(f"🔄 Current total: {total:.2f}% (aiming for 100%)")
            except ValueError:
                print("❌ Invalid input. Please enter a number.")

        # After all changes, validate total percentage
        if self.validatePercentages():

            # Sync latest percentages back to budgetDict before writing to Firestore

            self.saveBudget()
            print("\n🎯 All category percentages now total 100%. Changes saved!")
            self.viewBudget()
        else:
            print("\n⚠️ Percentages do not add up to 100%. Please review your budget.")

    #check that the chosen percentages add up to 100
    def validatePercentages(self):
        total = sum(getattr(self, key) for key in self.budgetKeys)
        if abs(total - 100) <= .001:
            return True
        else:
            print(f"\n⚠️ Budget percentages must total 100. Current total: {total}")
            return False
        
    #change budget based on $ amount
    def changeBudgetAmounts(self, income):
        print("\n Update multiple budget categories. Enter 0 to finish.")
        while True:
            key = self.chooseCategory()
            if not key:
                break

            try:
                new_amount = float(input(f"Enter new amount for {key}: "))
                percentage = (new_amount / income) * 100
                setattr(self, key, percentage)
                print(f"✅ {key.capitalize()} updated to ${new_amount}.")
                total = sum(getattr(self, key) for key in self.budgetKeys)
                print(f"🔄 Current total: ${total:.2f}. Aiming for ${income}")
            except ValueError:
                print("❌ Invalid input. Please enter a number.")

        final_total = sum(getattr(self, key) for key in self.budgetKeys)

        if abs(final_total - income) < 0.01:
            self.saveBudget()
            print(f"\n🎯 All category amounts now total ${income}. Changes saved!")
            self.viewBudget()
        else:
            print(f"\n⚠️ Amounts do not add up to ${income}. Please review your budget.")

    #save budget to firestore
    def saveBudget(self):
        for key in self.budgetKeys:
            self.budgetDict[key] = getattr(self, key)
        self.budgetDict["userId"] = self.userId
        if self.isBasicBudget == True:
            self.db.collection("budgets").document().create(self.budgetDict)
        else:
            self.db.collection("budgets").document(self.budgetId).set(self.budgetDict)

    #get budget amount set for a specific category and time period
    def getCategoryBudget(self, category, period):
        if period == "weekly":
            income = self.annIncome / 52
        elif period == "monthly":
            income = self.annIncome / 12
        elif period == "annual":
            income = self.annIncome
        categoryAmount = income * (self.budgetDict[category] / 100)
        return categoryAmount