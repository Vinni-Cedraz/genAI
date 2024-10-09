#!/usr/bin/env python3.12
import requests
import os
import json

# API URL
api_url = "http://127.0.0.1:5000"

# User credentials
email = "newuser@example.com"
password = "newuser_password"

# Register a new user
register_response = requests.post(
    f"{api_url}/register", json={"email": email, "password": password}
)

# Login the user and get the access token
login_response = requests.post(
    f"{api_url}/login", json={"email": email, "password": password}
)
access_token = login_response.json()["access_token"]

# Upload a PDF file
# with open("resumes/curriculo_1.pdf", "rb") as f:
#     upload_response = requests.post(
#         f"{api_url}/upload_pdf",
#         headers={"Authorization": f"Bearer {access_token}"},
#         files={"file": f},
#     )

# Get a list of all PDF files in the 'resumes/' directory
pdf_files = [f for f in os.listdir("resumes/") if f.endswith(".pdf")][:5]
# Upload each PDF file
for pdf_file in pdf_files:
    print(f"Uploading {pdf_file}...")
    with open(f"resumes/{pdf_file}", "rb") as f:
        upload_response = requests.post(
            f"{api_url}/upload_pdf",
            headers={"Authorization": f"Bearer {access_token}"},
            files={"file": f},
        )
        # check if the upload was successful
        print(upload_response.json())
        upload_response.raise_for_status()
        print(f"Uploaded {pdf_file} successfully.")

print(f"access token: {access_token}")

# Query for "python"
query_response = requests.get(
    f"{api_url}/search?query=Python",
    headers={"Authorization": f"Bearer {access_token}"},
)

# Test for the presence of "Python" in each dictionary's content
response_data = query_response.json()
total_tests = len(response_data)
passed_tests = 0

for item in response_data:
    if "Python" in item["content"]:
        passed_tests += 1

print("Response:\n\n\n", json.dumps(query_response.json(), indent=2, ensure_ascii=False))

print(f"passed {passed_tests} out of {total_tests} tests")
