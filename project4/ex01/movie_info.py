#!/usr/bin/env python3.10
import google.generativeai as genai
from dotenv import load_dotenv
import json
import os


load_dotenv("../.env")


movie_titles = [
    "The Matrix",
    "Inception",
    "Pulp Fiction",
    "The Shawshank Redemption",
    "The Godfather",
]


def string_to_dict(response: str) -> dict:
    """transforms a string in json format into a proper dictionary or json"""
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        return {}


def get_movie_info(movie_title: str) -> str:
    user_prompt = f"""
    Provide information about the movie "{movie_title}" in JSON format.
    Start your response with: {{ "title": "{movie_title}", """
    response = string_to_dict(send_to_gemini(instructions=user_prompt))
    return response


def send_to_gemini(instructions: str) -> str:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(instructions)
    return response.text


def main():
    for title in movie_titles:
        print(f"\nAnalyzing: {title}")
        result = get_movie_info(title)
        if result:
            for key, value in result.items():
                print(f"{key}: {value}")
        else:
            # Tratamento de erro adequado
            print("-" * 50)


if __name__ == "__main__":
    main()
