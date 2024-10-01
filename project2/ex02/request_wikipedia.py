#!/usr/bin/env python3.10

import requests
import sys
import mwparserfromhell
from typing import Dict


def create_file(input: str) -> str:
    """Creates a .txt file and returns its name."""
    filename = f"{input.replace(' ', '_')}.wiki"
    with open(filename, "w"):
        pass
    return filename


def search_wikipedia(input: str) -> Dict:
    """Input string on search in the wikipedia's API."""
    url = f"https://pt.wikipedia.org/w/api.php?action=opensearch&search={input}&limit=1&namespace=0&format=json"
    response = requests.get(url)
    data = response.json()
    if len(data[1]) > 0:
        title = data[1][0]  # Get the title of the first suggestion
        # Now get the content for the suggested title
        url = f"https://pt.wikipedia.org/w/api.php?action=query&prop=revisions&rvprop=content&format=json&titles={title}"
        response = requests.get(url)
        data = response.json()
    else:
        data = {}  # Return an empty dictionary if no suggestions were found
    return data


def remove_formatting(data: Dict) -> str:
    """Removes json and/or wiki Markup formatting."""
    if "query" not in data or "pages" not in data["query"]:
        return "No results found for the given search term."
    pages = data["query"]["pages"]
    page = pages[next(iter(pages))]
    wikitext = page["revisions"][0]["*"]
    wikicode = mwparserfromhell.parse(wikitext)
    text = wikicode.strip_code()
    return text


def save_to_file(filename: str, text: str):
    """Saves the result into the file."""
    with open(filename, "w") as f:
        f.write(text)


def main():
    if len(sys.argv) > 2:
        print(
            "Error: More than one string argument entered. Please enter only one string argument."
        )
        sys.exit(1)
    input = sys.argv[1]
    filename = create_file(input)
    data = search_wikipedia(input)
    text = remove_formatting(data)
    save_to_file(filename, text)


if __name__ == "__main__":
    main()
