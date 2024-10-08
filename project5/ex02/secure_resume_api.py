#!/usr/bin/env python3.10
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_jwt_extended import (
    JWTManager,
    jwt_required,
    create_access_token,
    get_jwt_identity,
)
from functools import wraps
import os
import PyPDF2
import chromadb
from chromadb.utils import embedding_functions
from langchain.text_splitter import RecursiveCharacterTextSplitter
import uuid
import logging
import json
from werkzeug.exceptions import TooManyRequests
from groq import Groq

UPLOAD_FOLDER = "./pdfs_posted/"
ALLOWED_EXTENSIONS = {"pdf"}
MAX_FILE_SIZE = 15 * 1024 * 1024  # 15MB

app = Flask(__name__)
app.json.ensure_ascii = False
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["JWT_SECRET_KEY"] = "your-secret-key"  # Change this!

jwt = JWTManager(app)
limiter = Limiter(get_remote_address, app=app, default_limits=["50 per minute"])

# chromadb setup:
persist_directory = "./chroma_data"
chroma_client = chromadb.PersistentClient(path=persist_directory)
func = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="paraphrase-multilingual-MiniLM-L12-v2"
)
collection = chroma_client.get_or_create_collection(
    name="curriculos", embedding_function=func
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Mock user database (replace with a real database in production)
users = {
    "admin@example.com": {
        "password": "admin_password",
        "role": "administrator",
        "id": str(uuid.uuid4()),
    },
    "recruiter@example.com": {
        "password": "recruiter_password",
        "role": "recruiter",
        "id": str(uuid.uuid4()),
    },
    "candidate@example.com": {
        "password": "candidate_password",
        "role": "candidate",
        "id": str(uuid.uuid4()),
    },
}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def role_required(allowed_roles):
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            current_user = get_jwt_identity()
            if current_user not in users:
                return jsonify({"msg": "User not found"}), 404
            user_role = users[current_user]["role"]
            if user_role not in allowed_roles:
                return jsonify({"msg": "Insufficient permissions"}), 403
            return fn(*args, **kwargs)

        return decorator

    return wrapper


@app.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    if email not in users or users[email]["password"] != password:
        return jsonify({"msg": "Invalid email or password"}), 401
    access_token = create_access_token(identity=email)
    return jsonify(access_token=access_token), 200


@app.route("/register", methods=["POST"])
def register():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    role = request.json.get("role", "candidate")
    if email in users:
        return jsonify({"msg": "Email already registered"}), 400
    users[email] = {
        "password": password,
        "role": role,
        "id": str(uuid.uuid4()),
    }  # Set role of new user
    return jsonify({"msg": "User registered successfully"}), 201


@app.route("/upload_pdf", methods=["POST"])
@limiter.limit("20/minute")
@jwt_required()
@role_required(["candidate", "administrator"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    if file and allowed_file(file.filename):
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(file_path)

        # Check file size
        if os.path.getsize(file_path) > MAX_FILE_SIZE:
            os.remove(file_path)
            return jsonify({"error": "File size exceeds limit"}), 400

        # Process the PDF
        with open(file_path, "rb") as f:
            pdf_reader = PyPDF2.PdfReader(f)
            text = ""
            for page_num in range(len(pdf_reader.pages)):
                text += pdf_reader.pages[page_num].extract_text()

            splitter = RecursiveCharacterTextSplitter(chunk_size=700, separators=[" "])
            chunks = splitter.split_text(text)

            # Store chunks in ChromaDB
            for i, chunk in enumerate(chunks, start=1):
                collection.add(
                    documents=[chunk],
                    ids=[f"{file.filename}_chunk_{i}"],
                    metadatas=[{"source": file.filename}],
                )

        return (
            jsonify(
                {
                    "message": f"PDF processed successfully, chunks created: {len(chunks)}"
                }
            ),
            201,
        )
    return jsonify({"error": "Invalid file type"}), 400


@app.route("/curriculum/<string:filename>", methods=["DELETE"])
@role_required(["administrator"])
def delete_curriculum(filename):
    collection = chroma_client.get_or_create_collection("curriculos")
    ids = collection.get(include=[])["ids"]
    if not any(filename in doc_id.split("_chunk_")[0] for doc_id in ids):
        return jsonify({"message": "Curriculum Not Found Within Database"}), 200
    try:
        for doc_id in ids:
            if filename in doc_id:
                collection.delete(ids=[doc_id])
        return jsonify({"message": "Curriculum deleted successfully"}), 200
    except Exception:
        return jsonify({"message": "Error deleting document"}), 500


@app.route("/user_info", methods=["GET"])
@jwt_required()
def user_info():
    current_user = get_jwt_identity()
    if current_user not in users:
        return jsonify({"msg": "User not found"}), 404
    user_data = users[current_user]
    return (
        jsonify(
            {"email": current_user, "role": user_data["role"], "id": user_data["id"]}
        ),
        200,
    )


@app.route("/search", methods=["GET"])
@limiter.limit("50/minute")
@jwt_required()
def search():
    query = request.args.get("query")
    results = collection.query(query_texts=[query], where_document={"$contains": query})
    response_data = []
    for i, result in enumerate(results["ids"][0]):
        content = results["documents"][0][i].replace("\n", " ").replace("•", " ")
        response_data.append(
            {
                "document": result.split("_chunk_")[0],
                "chunk": int(result.split("_chunk_")[1]),
                "content": content,
            }
        )

    return jsonify(response_data), 200


def query_groq(prompt):
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-8b-8192",
    )
    return chat_completion.choices[0].message.content


@app.route("/labeled", methods=["GET"])
@jwt_required()
def get_labeled_chunks():
    results = collection.get(include=["documents"])
    response_data = []
    for i, result in enumerate(results["ids"]):
        content = results["documents"][i].replace("\n", " ").replace("•", " ")
        response_data.append(
            {
                "document": result.split("_chunk_")[0],
                "chunk": int(result.split("_chunk_")[1]),
                "content": content,
                "name": "",
            }
        )

    for chunk in response_data:
        if chunk["chunk"] == 1:
            name = query_groq(
                f"""In the given chunk of text, Identify the name of the
                candidate, filtering out any extra information and return
                only their name and nothing else. Follow the example and
                do not include any extra information, only answer with
                a name and absolutely no other words, be extremely
                concise.
                <chunk>
                    {chunk["content"]}
                </chunk>
                <example>
                    <chunk>
                        "Diego Martins São Paulo, SP | (11) 9XXXX-XXXX | diego.martins@42sp.org.br Resumo Profissional Como Senior Cybersecurity Specialist, tenho 10 anos de experiência em liderar equipes de segurança  e  desenvolver  soluções  inovadoras  para  proteger  sistemas  e  dados.  Minha missão  é  utilizar  minhas  habilidades  técnicas  e  gerenciais  para  ajudar  organizações"
                    </chunk>
                    <your-answer>
                        Diego Martins
                    </your-answer>
                </example>
                """
            )
            chunk["name"] = name

    for chunk in response_data:
        if chunk["name"] != "":
            name = chunk["name"]
            doc_id = chunk["document"]
            for chunk in response_data:
                if chunk["document"] == doc_id:
                    chunk["name"] = name

    return jsonify(response_data), 200
    return results, 200


@app.errorhandler(TooManyRequests)
def handle_too_many_requests(e):
    return (
        jsonify({"error": "Limit of requestes exceeded. Try again later."}),
        429,
    )


@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response


if __name__ == "__main__":
    app.run(debug=False)
