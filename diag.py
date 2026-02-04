import os
from google.cloud import firestore

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'c:\Users\diieg\Desktop\DAM\PROYECTOS\Tanques\tanquesBACKEND\firebase-key.json'
db = firestore.Client()

print("--- USERS COLLECTION ---")
users = db.collection('users').stream()
for u in users:
    print(f"User ID: '{u.id}'")

print("\n--- SCORES COLLECTION (RECENT) ---")
scores = db.collection('scores').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(20).stream()
for s in scores:
    data = s.to_dict()
    print(f"Score: '{data.get('username')}' - {data.get('score')} - {data.get('timestamp')}")
