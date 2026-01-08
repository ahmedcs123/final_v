import os

db_path = "vines.db"
if os.path.exists(db_path):
    os.remove(db_path)
    print(f"Deleted {db_path} to reset credentials.")
else:
    print(f"{db_path} not found.")
