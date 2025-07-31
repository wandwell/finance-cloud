import pyrebase

from user_module import createUser

class AuthManager:
    def __init__(self):
        pyrebaseConfig = {
            "apiKey": "AIzaSyBFJCAQXIjOGqaA_LoDSaYp3sjmUaTcyWo",
            "databaseURL": "https://finance-537b6-default-rtdb.firebaseio.com",
            "authDomain": "finance-537b6.firebaseapp.com",
            "projectId": "finance-537b6",
            "storageBucket": "finance-537b6.firebasestorage.app",
            "messagingSenderId": "327934405329",
            "appId": "1:327934405329:web:46091a422342c6a91973f0"
        }
        firebase = pyrebase.initialize_app(pyrebaseConfig)
        self.auth = firebase.auth()
        self.user_id = None  # Will store userId after login/signup

    #allows user to login
    def login(self, email="", password=""):
        if not email:
            email = input("Email: ")
            password = input("Password: ")
        try:
            user = self.auth.sign_in_with_email_and_password(email, password)
            self.user_id = user["localId"]
            print("Login Successful")
            return self.user_id
        except:
            print("Invalid Username or Password. Please try again")

    #allows user to signup
    def signup(self):
        name = input("Name: ")
        email = input("Email: ")
        password = input("Password: ")
        try:
            user = self.auth.create_user_with_email_and_password(email, password)
            self.user_id = user["localId"]
            createUser(self.user_id, name, email)
            print("Signup Successful")
            self.login(email, password)
            return self.user_id
        except Exception as e:
            print(f"Error: {e}")
        
