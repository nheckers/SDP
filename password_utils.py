# password_utils.py
import bcrypt

# Function to hash passwords
def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

# Function to check if a given password matches the hashed one
import bcrypt

# Function to check if a given password matches the hashed one
def check_password(stored_hashed_password, password):
    """Ensure the stored hashed password is in bytes format before comparison."""
    # Ensure stored_hashed_password is in bytes (it might come as string from DB)
    if isinstance(stored_hashed_password, str):
        stored_hashed_password = stored_hashed_password.encode()  # Convert to bytes if it's a string

    return bcrypt.checkpw(password.encode(), stored_hashed_password)
