#!/usr/bin/env python3.10
import requests

# API URL
api_url = "http://127.0.0.1:5000"

# User credentials
email = "newuser@example.com"
password = "newuser_password"

# Register a new user
register_response = requests.post(f"{api_url}/register", json={"email": email, "password": password})

# Login the user and get the access token
login_response = requests.post(f"{api_url}/login", json={"email": email, "password": password})
access_token = login_response.json()['access_token']

# Upload a PDF file
with open('resumes/curriculo_1.pdf', 'rb') as f:
    upload_response = requests.post(f"{api_url}/upload_pdf", headers={"Authorization": f"Bearer {access_token}"}, files={"file": f})

response = requests.get(f"{api_url}/labeled", headers={"Authorization": f"Bearer {access_token}"})


