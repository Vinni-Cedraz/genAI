#!/usr/bin/env python3.10
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import sys


def get_response(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        sys.exit(1)
    except requests.exceptions.RequestException as err:
        print(f"Error occurred: {err}")
        sys.exit(1)
    return response


def get_first_link(url):
    response = get_response(url)
    soup = BeautifulSoup(response.text, "html.parser")
    content_div = soup.find(id="mw-content-text").find(class_="mw-parser-output")
    for elem in content_div.find_all(["p", "ul"], recursive=False):
        for link in elem.find_all("a"):
            if link.text.startswith("[") and link.text.endswith("]"):
                continue
            text_up_to_link = str(elem)[: str(elem).find(str(link))]
            if text_up_to_link.count("(") == text_up_to_link.count(")"):
                first_link = link.get("href")
                first_link = urljoin("https://en.wikipedia.org/", first_link)
                return first_link


def roads_to_philosophy(start_article: str):
    """Find the path from a start article to the
    Philosophy article on Wikipedia."""
    visited = set()
    current_article = f"https://en.wikipedia.org/wiki/{start_article}"
    while current_article not in visited:
        visited.add(current_article)
        print(f"current article: {current_article}")
        if "Philosophy" in current_article:
            print(f"{len(visited)} roads from {start_article} to Philosophy")
            return
        current_url = get_first_link(current_article)
        current_article = current_url
        if current_url is None:
            print(f"{current_article} leads to a dead end!")
            return
    current_article = current_url
    print(f"current article: {current_article}")
    print("It leads to an infinite loop!")
    return


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python roads_to_philosophy.py <start_article>")
    else:
        start_article = sys.argv[1].replace(" ", "_")
        roads_to_philosophy(start_article)
