#!/usr/bin/env python3.10
import requests
import json

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

# # Get a list of all PDF files in the 'resumes/' directory
# pdf_files = [f for f in os.listdir('resumes/') if f.endswith('.pdf')]
# # Upload each PDF file
# for pdf_file in pdf_files:
#     with open(f'resumes/{pdf_file}', 'rb') as f:
#         upload_response = requests.post(f"{api_url}/upload_pdf", headers={"Authorization": f"Bearer {access_token}"}, files={"file": f})

print(f"access token: {access_token}")

# Query for "python"
query_response = requests.get(f"{api_url}/search?query=Python", headers={"Authorization": f"Bearer {access_token}"})

# Print the query response as a JSON string
print(query_response.text)
