from firebase_admin import firestore

class AssetManager:
    def __init__(self, userId):
        self.userId = userId
        self.db = firestore.client()
        self.refreshAssets()

    def refreshAssets(self):
        query = self.db.collection("assets").where("userId", "==", self.userId)
        self.assets = list(query.stream())

    def listAssets(self):
        self.refreshAssets()
        if not self.assets:
            print("No assets found.")
            return

        print("\n📋 Your Assets:")
        for i, doc in enumerate(self.assets, start=1):
            asset = doc.to_dict()
            print(f"{i}. {asset['name']} | Type: {asset['type']} | Value: ${asset['value']:.2f}")

    def addAsset(self):
        print("\n➕ Add New Asset")
        name = input("Asset Name (e.g., Checking Account, Bitcoin): ").strip()
        asset_type = input("Asset Type (e.g., Bank, Crypto, Investment): ").strip()
        default = input("Is this your default account for transactions? (y/n): ").strip().lower()
        if default == "y":
            self.clearExistingDefault()
            default = "Y"
        else:
            default = "N"

        while True:
            try:
                value = float(input("Current Value: $"))
                if value < 0:
                    print("Value must be non-negative.")
                    continue
                break
            except ValueError:
                print("Please enter a valid number.")

        assetData = {
            "userId": self.userId,
            "name": name,
            "type": asset_type,
            "value": value,
            "default": default
        }

        self.db.collection("assets").document().create(assetData)
        print(f"✅ Added asset '{name}' worth ${value:.2f}.")
        self.refreshAssets()

    def chooseAsset(self):
        if not self.assets:
            print("No assets available.")
            return None

        print("\n📂 Choose an Asset:")
        for i, doc in enumerate(self.assets, start=1):
            asset = doc.to_dict()
            print(f"{i}. {asset['name']} | ${asset['value']:.2f}")
        print("0. Quit")

        try:
            choice = int(input("Enter asset number: "))
            if choice == 0:
                return None
            elif 1 <= choice <= len(self.assets):
                doc = self.assets[choice - 1]
                asset = doc.to_dict()
                asset["docId"] = doc.id
                return asset
            else:
                print("Invalid choice.")
                return None
        except ValueError:
            print("Please enter a valid number.")
            return None

    def editAsset(self, asset):
        print(f"\n✏️ Edit Asset: {asset['name']}")

        name = input(f"Current Name: {asset['name']} | New Name: ").strip() or asset["name"]
        asset_type = input(f"Current Type: {asset['type']} | New Type: ").strip() or asset["type"]
        default = input("Is this your default account for transactions? (y/n): ").strip().lower()
        if default == "y":
            self.clearExistingDefault()
            default = "Y"
        else:
            default = "N"

        while True:
            try:
                value = float(input(f"Current Value: ${asset['value']:.2f} | New Value: $"))
                if value < 0:
                    print("Value must be non-negative.")
                    continue
                break
            except ValueError:
                print("Please enter a valid number.")

        updatedData = {
            "userId": self.userId,
            "name": name,
            "type": asset_type,
            "value": value,
            "default": default
        }

        self.db.collection("assets").document(asset["docId"]).set(updatedData)
        print(f"✅ Asset '{name}' updated.")
        self.refreshAssets()

    def deleteAsset(self, asset):
        print(f"\n🗑️ Delete Asset: {asset['name']} (${asset['value']:.2f})")
        confirm = input("Are you sure you want to delete this asset? (y/n): ").strip().lower()
        if confirm == "y":
            self.db.collection("assets").document(asset["docId"]).delete()
            print("✅ Asset deleted.")
            self.refreshAssets()

    def clearExistingDefault(self):
        query = self.db.collection("assets").where("userId", "==", self.userId).where("default", "==", "Y")
        existing_defaults = list(query.stream())

        for doc in existing_defaults:
            asset = doc.to_dict()
            asset["default"] = "N"
            self.db.collection("assets").document(doc.id).set(asset)
            print(f"🔄 Removed default flag from '{asset['name']}'.")

    def updateByTransaction(self, amount, category):
        # Find default asset
        query = self.db.collection("assets").where("userId", "==", self.userId).where("default", "==", "Y")
        results = list(query.stream())

        if results:
            doc = results[0]
            account = doc.to_dict()
            account["docId"] = doc.id
        else:
            print("⚠️ No default account found. Please choose an asset manually.")
            account = self.chooseAsset()
            if not account:
                print("❌ No asset selected. Transaction update aborted.")
                return

        # Validate required fields
        if "value" not in account or "docId" not in account:
            print("❌ Asset data incomplete. Cannot update.")
            return

        currentValue = account["value"]

        # Update value based on transaction type
        if category == "income":
            newValue = currentValue + amount
        else:
            newValue = currentValue - amount

        # Ensure value doesn't go negative unless allowed
        if newValue < 0:
            print(f"⚠️ Warning: Asset '{account['name']}' will go negative (${newValue:.2f}).")

        # Update Firestore
        try:
            self.db.collection("assets").document(account["docId"]).update({"value": newValue})
            print(f"✅ Asset '{account['name']}' updated: ${currentValue:.2f} → ${newValue:.2f}")
            self.refreshAssets()
        except Exception as e:
            print(f"❌ Failed to update asset: {e}")
            

    def assetMenu(self):
        while True:
            choice = input(
                "\n💼 Asset Manager\n"
                "1. View Assets\n"
                "2. Add Asset\n"
                "3. Edit/Delete Asset\n"
                "4. Return to Main Menu\n"
                "Enter choice: "
            )

            if choice == "1":
                self.listAssets()
            elif choice == "2":
                self.addAsset()
            elif choice == "3":
                asset = self.chooseAsset()
                if asset:
                    sub = input("1. Edit\n2. Delete\n3. Cancel\nEnter choice: ")
                    if sub == "1":
                        self.editAsset(asset)
                    elif sub == "2":
                        self.deleteAsset(asset)
            elif choice == "4":
                print("Returning to Main Menu.")
                break
            else:
                print("Invalid choice.")