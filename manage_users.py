from werkzeug.security import generate_password_hash
from models import URLMapping, db, User

def add_user(username, password):
    """Adds a new user to the database."""
    from app import app

    with app.app_context():
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"User '{username}' already exists.")
            return

        hashed_password = generate_password_hash(password)

        new_user = User(username=username, password=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        print(f"User '{username}' added successfully.")

def delete_user(username):
    """Deletes an existing user from the database."""
    from app import app

    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f"User '{username}' does not exist.")
            return

        # Handle related records in the url_mapping table
        related_urls = URLMapping.query.filter_by(user_id=user.id).all()
        for url in related_urls:
            db.session.delete(url)  # or update as needed

        db.session.delete(user)
        db.session.commit()

        print(f"User '{username}' and all related records deleted successfully.")

def list_users():
    """Lists all users in the database."""
    from app import app

    with app.app_context():
        users = User.query.all()
        if not users:
            print("No users found.")
            return

        print("List of users:")
        for user in users:
            print(f"- {user.username}")

if __name__ == "__main__":
    while True:
        print("\n--- User Management ---")
        print("1. Add User")
        print("2. Delete User")
        print("3. List Users")
        print("4. Exit")
        choice = input("Choose an option: ")

        if choice == '1':
            username = input("Enter username: ")
            password = input("Enter password: ")
            add_user(username, password)
        elif choice == '2':
            username = input("Enter username to delete: ")
            delete_user(username)
        elif choice == '3':
            list_users()
        elif choice == '4':
            print("Exiting...")
            break
        else:
            print("Invalid choice, please try again.")
