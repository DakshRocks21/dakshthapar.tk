from werkzeug.security import generate_password_hash
from models import db, User

def add_user(username, password):
    from app import app 

    with app.app_context():
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"User {username} already exists.")
            return

        hashed_password = generate_password_hash(password)

        new_user = User(username=username, password=hashed_password)

        db.session.add(new_user)
        db.session.commit()
        
        print(f"User {username} added successfully.")

if __name__ == "__main__":
    username = input("Enter username: ")
    password = input("Enter password: ")
    
    add_user(username, password)
