"""Authentication service for user management."""
import bcrypt
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import DatabaseManager

class AuthService:
    """Handles user authentication and registration."""
    
    def __init__(self):
        """Initialize the auth service."""
        self.db_manager = DatabaseManager()
    
    def register_user(self, first_name, last_name, username):
        """Register a new user with auto-generated password."""
        # Check if username already exists
        existing_user = self.db_manager.get_user_by_username(username)
        if existing_user:
            return False, "Username already exists."
        
        # Generate a password from first_name and last_name
        password = f"{first_name.lower()}{last_name.lower()}123"
        
        # Hash the password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create the user
        try:
            user_id = self.db_manager.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                password_hash=password_hash
            )
            return True, {"user_id": user_id, "password": password}
        except Exception as e:
            return False, str(e)
    
    def login(self, username, password):
        """Authenticate a user."""
        user = self.db_manager.get_user_by_username(username)
        if not user:
            return False, "Invalid username or password."
        
        # Check password
        if bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            return True, {
                "user_id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username
            }
        else:
            return False, "Invalid username or password."
    
    def get_user_info(self, user_id):
        """Get user information by ID."""
        user = self.db_manager.get_user_by_id(user_id)
        if user:
            return {
                "user_id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username
            }
        return None