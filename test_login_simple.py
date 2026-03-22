import requests

BASE_URL = "http://localhost:8000/api/auth"

def test_login():
    # Attempt to login with the user we just created in the previous test
    # (or create a new one to be sure)
    username = "testuser_debug"
    email = "test@example.com"
    password = "password123"
    
    # 1. Signup
    print(f"Signup for {email}...")
    res = requests.post(f"{BASE_URL}/signup", json={
        "username": username,
        "email": email,
        "password": password
    })
    print("Signup Status:", res.status_code)
    
    # 2. Login
    print(f"Login for {email}...")
    res = requests.post(f"{BASE_URL}/login", json={
        "email": email,
        "password": password
    })
    print("Login Status:", res.status_code)
    print("Login Response:", res.text)

if __name__ == "__main__":
    test_login()
