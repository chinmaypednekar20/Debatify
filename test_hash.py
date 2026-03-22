from passlib.context import CryptContext
import traceback

try:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    password = "password123"
    print(f"Hashing password: {password}")
    hashed = pwd_context.hash(password)
    print(f"Hashed: {hashed}")
    
    verified = pwd_context.verify(password, hashed)
    print(f"Verified: {verified}")
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()
