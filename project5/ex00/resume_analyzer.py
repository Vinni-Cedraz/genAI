#!/usr/bin/env python3.10
import os
import chromadb
from chromadb.utils import embedding_functions
from PyPDF2 import PdfReader
import re


def process_pdf_directory(pdf_directory, collection):
    pdf_files = [f for f in os.listdir(pdf_directory) if f.endswith(".pdf")]
    print(f"Encontrados {len(pdf_files)} arquivos PDF no diretório.")
    existing_ids = set(collection.get()["ids"])
    for i, pdf_file in enumerate(pdf_files, start=1):
        doc_id = f"doc_{pdf_file}"
        if doc_id in existing_ids:
            print(f"Pulando PDF já processado {i}/{len(pdf_files)}: {pdf_file}")
            continue
        print(f"Processando PDF {i}/{len(pdf_files)}: {pdf_file}")
        with open(os.path.join(pdf_directory, pdf_file), "rb") as f:
            reader = PdfReader(f)
            document = ""
            for page in range(len(reader.pages)):
                document += reader.pages[page].extract_text()
            metadata = {"source": pdf_file}
            collection.add(
                documents=[document],
                metadatas=[metadata],
                ids=[doc_id],
            )
            print(f"- Documento {pdf_file} processado e armazenado.")
    print("Processamento de todos os PDFs concluído.")


def interactive_query_loop(collection):
    print("Processamento concluído. Iniciando modo de consulta.")
    while True:
        query = input("\nDigite sua consulta ou 'sair' para encerrar.\nConsulta: ")
        if query.lower() == "sair":
            break
        results = collection.query(query_texts=[query], n_results=10)
        print("\nResultados:")
        result_count = 0
        for doc, metadata in zip(results["documents"][0], results["metadatas"][0]):

            # Create a regex pattern to match whole words only
            pattern = r"\b" + re.escape(query) + r"\b"
            matches = list(re.finditer(pattern, doc, re.IGNORECASE))
            match_count = len(matches)

            if match_count > 0:
                result_count += 1
                print(f"Resultado {result_count}:")
                print(f"Documento: {metadata['source']}")
                print(f"Número de correspondências exatas: {match_count}")
                if matches:
                    start = max(0, matches[0].start() - 100)
                    end = min(len(doc), matches[0].end() + 100)
                    excerpt = doc[start:end]
                    print(f"Trecho: ...{excerpt}...")
                print()
        if result_count == 0:
            print("Nenhum resultado exato encontrado.")


def main():
    persist_directory = "./chroma_data"
    pdf_directory = "./pdfs"
    chroma_client = chromadb.PersistentClient(path=persist_directory)
    func = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="paraphrase-multilingual-MiniLM-L12-v2"
    )
    collection = chroma_client.get_or_create_collection(
        name="curriculos", embedding_function=func
    )
    process_pdf_directory(pdf_directory, collection)
    interactive_query_loop(collection)


if __name__ == "__main__":
    main()
