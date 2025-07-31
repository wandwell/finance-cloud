from firebase_admin import firestore

#create user
def createUser(userId, name, email):
    db = firestore.client()
    try:
        userData = {
            "name": name,
            "email": email,
        }

        db.collection("users").document(userId).set(userData)
    except Exception as e:
        print(f"Signup error:", e)
        return None

#fetch user by id from firestore database
def getUser(userId):
    db = firestore.client()
    userDoc = db.collection("users").document(userId).get()
    if userDoc.exists:
        return userDoc.to_dict()
    else:
        print("User not found.")
        return None