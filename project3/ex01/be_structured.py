#!/usr/bin/env python3.10
from groq import Groq
import os
import subprocess
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


def format_prompt(job_description):
    prompt = f"""
    You are an assistant specialized in analyzing job descriptions.
    Extract the following information from the provided description:
    - Name of role
    - Working hours
    - Country
    - Tech skills

    Job description:
    {job_description}
    """
    return prompt


def query_groq(prompt):
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-8b-8192",
    )
    return chat_completion.choices[0].message.content


def query_google(prompt):
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text


def query_qwen(prompt):
    arg = ["ollama", "run", "qwen2:1.5b", prompt]
    result = subprocess.run(arg, stdout=subprocess.PIPE, check=True)
    return result.stdout.decode('utf-8')


def query_all_models(prompt):
    return {
        "google": query_google(prompt),
        "qwen": query_qwen(prompt),
        "groq": query_groq(prompt),
    }


def main():
    with open("job_description.txt", "r") as file:
        job_description = file.read()
    formatted_prompt = format_prompt(job_description)
    results = query_all_models(formatted_prompt)
    for model, response in results.items():
        print(f"\nAnálise do {model}:")
        print(response)
        print("-" * 50)


if __name__ == "__main__":
    main()
