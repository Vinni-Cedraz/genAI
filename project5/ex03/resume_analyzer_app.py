#!/usr/bin/env python3.10
import streamlit as st
import requests
import os
from groq import Groq
from collections import defaultdict

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
if "search" not in st.session_state:
    st.session_state.search = None
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


def create_xml_context(data):
    result = ""
    for name, content_list in data.items():
        content = " ".join(content_list)
        content = content.strip()
        result += f"<{name}_skills>{content}</{name}_skills>"
    return result


# SEMANTIC SEARCH:
search_query = st.text_input("Pesquisar por habilidades:")
if st.button("Pesquisar"):
    response = requests.get(
        f"{api_url}/search?query={search_query}",
        params={"query": search_query},
        headers=headers,
    )
    if response.status_code == 200:
        st.session_state.search = response.json()
    else:
        st.error("Erro ao realizar a pesquisa")

    content_grouped_by_candidate_name = defaultdict(list)
    for chnk in st.session_state.search:
        content_grouped_by_candidate_name[chnk["name"]].append(chnk["content"])

    context = create_xml_context(content_grouped_by_candidate_name)

    print("xml context: " + context)
    sys_prompt = f"""
        Follow the intructions within the xml tags below:
        <role>
            You are a resume analyzer machine. You'll receive a query and
            a context. The context has candidates with skills that are probably
            related to the query. Look for the candidates that have the skill
            specified by the query and sumarize their skills.
        </role>
        <rules>
        - Completely ignore the candidates that don't have the skill
        specified by the query. Don't mention their names AT ALL.
        - The query should be a skill, such as "Python" or "leadership", if
        it's not a skill, politely decline the request and guide them back to
        the main topic: candidate skills.
        - Your answer will ALWAYS be in Brazilian Portuguese.
        - Always start your answers with: "Resumo das habilidades em
        <query> de cada candidato:", unless the query is not related to the
        main topic.
        - Do not ask follow up questions.
        - You'll receive context in the following format:
        <candidate_name><skills>text here</skills></candidate_name>
        - You should follow the examples.
        </rules>
        <context>
            {context}
        </context>
        <query>
            {search_query}
        </query>
        <examples>
        <correct_query_example>
            <query>
               Java
            </query>
            <your_answer>
                Resumo das habilidades em Java de cada candidato:
                    ...rest of the answer....
            </your_answer>
        </correct_query_example>
        <unrelated_query_example>
            <query>
                Quem foi Thomas Jefferson?
            </query>
            <your_answer>
                Por favor, apenas faça perguntas sobre as
                habilidades dos candidatos.
            </your_answer>
        </unrelated_query_example>
        </examples>
        <VERY_IMPORTANT_INSTRUCTION>
            Suppose you have a context with 10 candidate names but you don't
            find the query skills in three of them: Lucas Alves, Ana Costa and
            Silvana Reis. In that case, those three names should not be present
            in your answer at all. So the following sentences would be
            unacceptable to be found in your answer:
            <answer>
                Lucas Alves: Não menciona habilidades em Python.
                Ana Costa: Não menciona habilidades em Python.
                Silvana Reis: Nenhuma informação sobre Python foi encontrada em
                seu currículo.
            </answer>
            Because if a candidate doesn't mention a query skill, you should
            completely ignore that candidate, not mentioning their name at all.
        </VERY_IMPORTANT_INSTRUCTION>
        """
    # feed the result of the search to the model as context
    llm_response = query_groq(sys_prompt)
    st.write(llm_response)
