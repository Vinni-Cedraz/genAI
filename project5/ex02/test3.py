#!/usr/bin/env python3.10
import requests
import json

# Define the URL
url = "http://localhost:5000"

# Define the admin credentials
admin_credentials = {
    "email": "admin@example.com",
    "password": "admin_password"
}

# Login as admin
response = requests.post(f"{url}/login", json=admin_credentials)
access_token = response.json()['access_token']

# Define headers for subsequent requests
headers = {
    'Authorization': f'Bearer {access_token}'
}

# Define a PDF file to POST
file_path = "resumes/curriculo_45.pdf"
files = {'file': open(file_path, 'rb')}

# POST a document
response = requests.post(f"{url}/upload_pdf", files=files, headers=headers)
print("POST response:", response.json())

# Perform a search
search_params = {'query': 'your_search_query'}
response = requests.get(f"{url}/search?query=Tableau", params=search_params, headers=headers)
