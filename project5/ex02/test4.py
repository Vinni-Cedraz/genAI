#!/usr/bin/env python3.10
import requests

# Replace with the actual URL of your Flask application
base_url = "http://localhost:5000"

# Register a new candidate
register_response = requests.post(
    f"{base_url}/register",
    json={
        "email": "candidate12@example.com",
        "password": "candidate_password",
        "role": "candidate",
    },
)

# Check if registration was successful
if register_response.status_code != 201:
    print(f"Registration failed: {register_response.json()}")
    exit(1)

# Log in as the new candidate
login_response = requests.post(
    f"{base_url}/login",
    json={"email": "candidate@example.com", "password": "candidate_password"},
)

# Check if login was successful
if login_response.status_code != 200:
    print(f"Login failed: {login_response.json()}")
    exit(1)

# Get the candidate's token
candidate_token = login_response.json()["access_token"]

headers = {"Authorization": f"Bearer {candidate_token}"}

# The filename to delete
filename = "curriculo_12.pdf"

response = requests.delete(f"{base_url}/curriculum/{filename}", headers=headers)

# Print the HTTP status code and response body
print(f"Response Body: {response.json()}")
print(f"Status Code: {response.status_code}")
