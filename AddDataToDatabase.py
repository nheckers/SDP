import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL':"https://sdp2024-6ca30-default-rtdb.firebaseio.com/"
})


ref = db.reference('People')

data = {
    "Hadas":
        {
            "name": "Hadas Ben-Noun",
            "user_id": "41401",
            "role": "Vistor",
            "access_level": "restricted_access",
            "last_visit_time": "2024-10-21 00:54:34",
            "visit_history": ["2024-10-21 00:54:34", "2024-09-14 10:21:18"],
            "photo_id": "Images/Hadas.png",
            "status": "active",
            "attendance": 5
        },
    "Victor":
        {
            "name": "Victor idk",
            "user_id": "7901",
            "role": "Resident",
            "access_level": "restricted_access",
            "last_visit_time": "2024-10-21 09:54:34",
            "visit_history": ["2024-10-21 11:54:34", "2024-09-14 10:21:18"],
            "photo_id": "Images/Victor.png",
            "status": "active",
            "attendance": 6
        }
}

for key,value in data.items():
    ref.child(key).set(value)