#!/usr/bin/env python3.10
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
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

    print("Response:", json.dumps(response_data, indent=2, ensure_ascii=False))
    response = jsonify(response_data)
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response, 200


@app.route("/upload_pdf", methods=["POST"])
@limiter.limit("20/minute")
@jwt_required()
@role_required(["candidate", "administrator"])
def upload_file():
    current_user = get_jwt_identity()
    user_id = users[current_user]["id"]

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

            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, separators=[" "])
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
    except:
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


@app.route("/document_ids", methods=["GET"])
@jwt_required()
@role_required(["administrator"])
def get_document_ids():
    # Query the database
    collection = chroma_client.get_or_create_collection(name="curriculos")
    # get all document IDs
    document_ids = collection.get(include=[])["ids"]
    # Remove the chunk number from the IDs
    document_ids = [id.split("_chunk_")[0] for id in document_ids]
    # Remove duplicates
    document_ids = list(set(document_ids))
    return jsonify(document_ids), 200


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
