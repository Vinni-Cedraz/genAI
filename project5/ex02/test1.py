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

# # Get a list of all PDF files in the 'resumes/' directory
# pdf_files = [f for f in os.listdir("resumes/") if f.endswith(".pdf")]
# # Upload each PDF file
# for pdf_file in pdf_files:
#     print(f"Uploading {pdf_file}...")
#     with open(f"resumes/{pdf_file}", "rb") as f:
#         upload_response = requests.post(
#             f"{api_url}/upload_pdf",
#             headers={"Authorization": f"Bearer {access_token}"},
#             files={"file": f},
#         )
#         # check if the upload was successful
#         print(upload_response.json())
#         upload_response.raise_for_status()
#         print(f"Uploaded {pdf_file} successfully.")

# print(f"access token: {access_token}")

java_coders = [
    "Diego Martins",
    "Larissa Silva",
    "Bruno Carvalho",
    "Gustavo Santos",
    "Bruno Costa",
    "Beatriz Oliveira",
    "Pedro Lima",
    "Bruno Souza",
    "Beatriz Gomes",
    "Juliana Ferreira",
    "Ana Ferreira",
    "Rafael Almeida",
    "Maria Almeida",
    "Beatriz Ribeiro",
]

query = "Java"
query_response = requests.get(
    f"{api_url}/search?query={query}",
    headers={"Authorization": f"Bearer {access_token}"},
)

response_data = query_response.json()

print(
    "Response:\n\n\n", json.dumps(query_response.json(), indent=2, ensure_ascii=False)
)

total_tests = len(response_data)
passed_tests = 0

for item in response_data:
    if query in item["content"]:
        passed_tests += 1

print(
    f"chunk relevance test: passed {passed_tests} out of {
        total_tests}, for query {query}"
)


passed_tests = 0
response_names = list(set(res["name"] for res in response_data))
total_tests = len(response_names)

for name in java_coders:
    if name in response_names:
        passed_tests += 1

print(
    f"""expected to find {len(java_coders)} candidates in response, found {
        passed_tests}"""
)
