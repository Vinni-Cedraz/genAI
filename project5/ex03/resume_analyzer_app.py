#!/usr/bin/env python3.10
import streamlit as st
import requests
import os
from groq import Groq


st.title("Análise de currículos")
api_url = "http://127.0.0.1:5000"


def query_groq(prompt):
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-8b-8192",
    )
    return chat_completion.choices[0].message.content


# Initialize session state
if "access_token" not in st.session_state:
    st.session_state.access_token = None
# Initialize session state
if "search_results" not in st.session_state:
    st.session_state.search_results = None
# Initialize session_state for files_to_be_uploaded
if "files_to_be_uploaded" not in st.session_state:
    st.session_state.files_to_be_uploaded = True


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
    except KeyError:
        st.error("E-mail ou senha inválidos")


# FILE UPLOAD SECTION
if st.session_state.access_token:
    files = st.file_uploader(
        "Envie os currículos dos candidatos", accept_multiple_files=True
    )
    headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
    if files and st.session_state.files_to_be_uploaded:
        for file in files:
            upload_response = requests.post(
                f"{api_url}/upload_pdf",
                headers=headers,
                files={"file": file},
            )
            if upload_response.status_code == 201:
                st.success(f"{file.name} enviado com sucesso")
            else:
                st.error(f"Erro ao enviar {file.name}")
        st.session_state.files_to_be_uploaded = False
else:
    st.write("Please log in to upload files.")


# SEMANTIC SEARCH:
search_query = st.text_input("Pesquisar por habilidades:")
if st.button("Pesquisar"):
    response = requests.get(
        f"{api_url}/search?query={search_query}",
        params={"query": search_query},
        headers=headers,
    )
    if response.status_code == 200:
        st.session_state.search_results = response.json()
    else:
        st.error("Erro ao realizar a pesquisa")

    # RETRIEVAL AUGMENTED GENERATION:
    # create prompt
    if st.session_state.search_results is not None:
        context = " ".join(
            [result["content"] for result in st.session_state.search_results]
        )

    sys_prompt = f"""
    Follow the intructions within the xml tags below:
    <role>
        You are a resume analyzer, you answer queries about the resume of
        a candidate.
    </role>
    <rules>
    - The context is a chunk of the resume of a candidate.
    - Provide an answer based on the information found about the query within
    the context.
    - If the answer is not available in the context, respond with
    'I don't know'.
    - If the user asks for something outside of the context of curriculum
    analysis, politely decline the request and guide them back to
    the main topic.
    - Do not ask follow up questions.
    - Start your answers with "The candidate "
    - Never use xml tags on your answers.
    </rules>
    <context>
        {context}
    </context>
    <query>
        {search_query}
    </query>
    """

    if not st.session_state.search_results:
        st.write(
            """The candidate's resume doesn't have
            any content related to your query"""
        )
    else:
        # feed the result of the search to the model as context
        llm_response = query_groq(sys_prompt)
        st.write(llm_response)
