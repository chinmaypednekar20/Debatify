import requests
import string
import random

BASE_URL = "http://localhost:8000/api/auth"

def rstr(length=8):
    return "".join(random.choices(string.ascii_lowercase, k=length))

def test_auth():
    username = f"user_{rstr()}"
    email = f"{username}@example.com"
    password = "password123"

    print(f"Testing signup for {email}...")
    res = requests.post(f"{BASE_URL}/signup", json={
        "username": username,
        "email": email,
        "password": password
    })
    print("Signup Status:", res.status_code)
    print("Signup Response:", res.text)

    if res.status_code != 200:
        return

    print(f"\nTesting login for {email}...")
    res = requests.post(f"{BASE_URL}/login", json={
        "email": email,
        "password": password
    })
    print("Login Status:", res.status_code)
    print("Login Response:", res.text)

if __name__ == "__main__":
    test_auth()
