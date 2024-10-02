#!/usr/bin/env python3.10
import requests
import sys

# API base URL
base_url = "http://127.0.0.1:5000"

if len(sys.argv) < 3:
    print("Usage: script.py <admin_email>")
    sys.exit(1)

# Create an admin user
admin_email = sys.argv[1]
curriculum = sys.argv[2]
admin_password = "_admin_password"
admin_role = "administrator"


try:
    register_url = f"{base_url}/register"
    register_data = {
        "email": admin_email,
        "password": admin_password,
        "role": admin_role,
    }

    register_response = requests.post(register_url, json=register_data)
    register_response.raise_for_status()
    print("Admin user created successfully.")
except requests.exceptions.HTTPError as err:
    print(f"Failed to create admin user: {err}")
    exit(1)


# Login as the admin user
try:
    login_url = f"{base_url}/login"
    login_data = {"email": admin_email, "password": admin_password, "role": admin_role}

    login_response = requests.post(login_url, json=login_data)
    login_response.raise_for_status()
    access_token = login_response.json()["access_token"]
    print("Admin user logged in successfully.")
except requests.exceptions.HTTPError as err:
    print(f"Failed to login as admin user: {err}")
    exit(1)


# Delete the document by name
document_name = f"curriculo_{sys.argv[2]}.pdf"
try:
    delete_url = f"{base_url}/curriculum/{document_name}"
    headers = {"Authorization": f"Bearer {access_token}"}
    delete_response = requests.delete(delete_url, headers=headers)
    print(f"delete response (supposed to be a json): {delete_response.json()}")
    delete_response.raise_for_status()
except requests.exceptions.HTTPError as err:
    print(f"Failed to delete document {document_name}: {err}")
    exit(1)
