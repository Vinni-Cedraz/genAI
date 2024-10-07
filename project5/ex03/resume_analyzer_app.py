#!/usr/bin/env python3.10
import streamlit as st
import requests
import json

st.title("Análise de currículos")
api_url = "http://127.0.0.1:5000"

# Initialize session state
if "access_token" not in st.session_state:
    st.session_state.access_token = None

# User credentials
email = st.text_input("E-mail:")
password = st.text_input("Senha:", type="password")

# REGISTER A NEW USER:
if st.button("Cadastrar"):
    register_response = requests.post(
        f"{api_url}/register", json={"email": email, "password": password}
    )
    if register_response.status_code == 400:
        st.error("Usuário já cadastrado")
    else:
        st.success("Usuário cadastrado com sucesso")

# LOGIN THE USER AND GET THE ACCESS TOKEN
if st.button("Login"):
    login_response = requests.post(
        f"{api_url}/login", json={"email": email, "password": password}
    )
    try:
        st.session_state.access_token = login_response.json()["access_token"]
        st.success("Login successful")
        print("DEBUG: Login successful, access token obtained")
    except KeyError:
        st.error("E-mail ou senha inválidos")
        print("DEBUG: Login failed")

# File upload section
if st.session_state.access_token:
    print("DEBUG: Access token is present")
    files = st.file_uploader(
        "Envie os currículos dos candidatos", accept_multiple_files=True
    )
    print(f"DEBUG: Uploaded file: {files}")

    if files:
        for file in files:
            print(f"DEBUG: File name: {file.name}")
            upload_response = requests.post(
                f"{api_url}/upload_pdf",
                headers={"Authorization": f"Bearer {st.session_state.access_token}"},
                files={"file": file},
            )
            print(f"DEBUG: Upload response status code: {upload_response.status_code}")

            if upload_response.status_code == 201:
                st.success(f"{file.name} enviado com sucesso")
                print(f"DEBUG: Server response: {upload_response.json()}")
            else:
                st.error(f"Erro ao enviar {file.name}")
                print(f"DEBUG: Error response: {upload_response.text}")
else:
    st.write("Please log in to upload files.")
    print("DEBUG: No access token, user needs to log in")
