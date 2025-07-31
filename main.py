import firebase_admin
from firebase_admin import credentials, firestore
from auth_module import AuthManager
from user_module import getUser
from budget_module import Budget
from transaction_module import TransactionManager
from asset_module import AssetManager

# Firebase Admin SDK (for Firestore)
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

#Authentication
auth_manager = AuthManager()

# menu
def showMainMenu(user_id):
    budget = Budget(user_id)
    transactionManager = TransactionManager(user_id)
    assetManager = AssetManager(user_id)
    user = getUser(user_id)
    while True:
        print(f"Welcome {user['name']}")
        menuInput = input("1. Budget Manager \n2. Transaction Manager \n3. Asset Manager \n4. Quit\n")

        if menuInput == "1":
            budget.viewBudget()
        elif menuInput == "2":
            transactionManager.transactionMenu()
        elif menuInput == "3":
            assetManager.assetMenu()
        elif menuInput == "4":
            print("Thanks for using the Finance Manager!")
            break
        else:
            print("Invalid input. Please try again.")

def main():
    authInput = input("Please choose from the following options \n1: Login \n2: Signup \n3: Quit \n")
    user_id = None

    if authInput == "1":
        user_id = auth_manager.login()
    elif authInput == "2":
        user_id = auth_manager.signup()
    elif authInput == "3":
        print("Have a Great Day!")
        return
    else:
        print("Invalid Option.")
        return

    if user_id:
        showMainMenu(user_id)
    else:
        print("Authentication failed. Please try again.")
    
#Call Main
main()