#!/usr/bin/env python3.10
import google.generativeai as genai
from dotenv import load_dotenv
import os
import re


load_dotenv("../.env")


def send_to_gemini(instructions: str) -> str:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(instructions)
    return response.text


def run_prompt_chain():
    # Define the prompts for each analysis step
    prompt1 = "<instruction>Tell me about the life and career of Claude Shannon. Format the answer inside of <answer1></answer1> xml tags.</instruction>"
    prompt2 = "<instruction>What were Claude Shannon's main contributions to information theory? Format the answer inside of <answer2></answer2> xml tags. </instruction>"
    prompt3 = "<instruction>What impact did Claude Shannon's work have on modern computing and communication technologies? Format the answer inside of <answer3></answer3> xml tags.</instruction>"
    prompt4 = "<instruction>Summarize the information from the previous steps into a comprehensive analysis of Claude Shannon (between 200 and 300 words). Format the answer inside of <answer4></answer4> xml tags.</instruction>"
    prompt5 = "<instruction>Translate the final answer to Brazilian Portuguese. Format the answer inside of <answer5></answer5> xml tags.</instruction>"

    answer1 = send_to_gemini(prompt1)
    answer2 = send_to_gemini(
        f"""{prompt2}
                            <context>
                                <life_and_career>
                                    {extract_content(answer1, 'answer1')}
                                </life_and_career>
                            </context>"""
    )
    answer3 = send_to_gemini(
        f"""{prompt3}
                             <context>
                                <life_and_career>
                                    {extract_content(answer1, 'answer1')}
                                </life_and_career>
                                <contribution_to_information_theory>
                                    {extract_content(answer2, "answer2")}
                                </contribution_to_information_theory>
                            </context>"""
    )
    answer4 = send_to_gemini(
        f"""{prompt4}
                            <context>
                                <life_and_career>
                                    {extract_content(answer1, "answer1")}
                                </life_and_career>
                                <contribution_to_information_theory>
                                    {extract_content(answer2, "answer2")}
                                </contribution_to_information_theory>
                                <impact_on_modern_computing_and_communication_technologies>
                                    {extract_content(answer3, "answer3")}
                                </impact_on_modern_computing_and_communication_technologies>
                            </context>
    """
    )
    answer5 = send_to_gemini(
        f"{prompt5} <context>{extract_content(answer4, 'answer4')}</context>"
    )
    print(extract_content(answer5, "answer5"))


def extract_content(text, tag):
    pattern = f"<{tag}>(.*?)</{tag}>"
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1).strip() if match else ""


def main():
    run_prompt_chain()


if __name__ == "__main__":
    main()
