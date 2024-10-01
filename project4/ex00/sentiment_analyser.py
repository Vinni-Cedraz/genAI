#!/usr/bin/env python3.10

import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv("../.env")


github_comments = [
    {
        "text": "Ótimo trabalho na implementação desta feature! O código está limpo e bem documentado. Isso vai ajudar muito nossa produtividade.",
        "sentiment": "",
    },
    {
        "text": "Esta mudança quebrou a funcionalidade X. Por favor, reverta o commit imediatamente.",
        "sentiment": "",
    },
    {
        "text": "Podemos discutir uma abordagem alternativa para este problema? Acho que a solução atual pode causar problemas de desempenho no futuro.",
        "sentiment": "",
    },
    {
        "text": "Obrigado por relatar este bug. Vou investigar e atualizar a issue assim que tiver mais informações.",
        "sentiment": "",
    },
    {
        "text": "Este pull request não segue nossas diretrizes de estilo de código. Por favor, revise e faça as correções necessárias.",
        "sentiment": "",
    },
    {
        "text": "Excelente ideia! Isso resolve um problema que estávamos enfrentando há semanas. Mal posso esperar para ver isso implementado.",
        "sentiment": "",
    },
    {
        "text": "Esta issue está aberta há meses sem nenhum progresso. Podemos considerar fechá-la se não for mais relevante?",
        "sentiment": "",
    },
    {
        "text": "O novo recurso está causando conflitos com o módulo Y. Precisamos de uma solução urgente para isso.",
        "sentiment": "",
    },
    {
        "text": "Boa captura! Este edge case não tinha sido considerado. Vou adicionar testes para cobrir este cenário.",
        "sentiment": "",
    },
    {
        "text": "Não entendo por que estamos priorizando esta feature. Existem problemas mais críticos que deveríamos estar abordando.",
        "sentiment": "",
    },
]


def generate_prompt(text):
    prompt = f"""
    Siga as instruções detalhadas para você nas instruções abaixo, o
    texto dentro das tags xml são para sua própria instrução e não devem estar
    presentes em sua resposta:
        <instruções>
        <papel> Você é um bot analisador de sentimentos. </papel>
        <tarefa> Analisar o sentimento de comentários em português brasileiro
        no contexto de desenvolvimento de software seguindo as regras </tarefa>
        <regras>
            <regra1>
                Sempre responda com uma única palavra.
            </regra1>
            <regra2>
                Sua resposta deve ser sempre em português.
            </regra2>
            <regra3>
                Sua resposta sempre será "Positivo" para um comentário positivo sobre solucoes
                ou "Negativo" para um comentário relatando problemas ou reclamações
            </regra3>
        </regras>
        <exemplos>
            <exemplo1>
                Comentário: Ótimo trabalho na implementação desta feature! O
                código está limpo e bem documentado. Isso vai ajudar muito
                nossa produtividade.
                Sua Resposta: "Positivo"
            </exemplo1>
            <exemplo2>
                Comentário: Esta mudança quebrou a funcionalidade X. Por favor,
                reverta o commit imediatamente.
                Sua Resposta: "Negativo"
            </exemplo2>
            <exemplo3>
                Comentário: "Este pull request não segue nossas diretrizes de
                estilo de código. Por favor, revise e faça as correções
                necessárias."
                Sua Resposta: "Negativo"
            </exemplo3>
            <exemplo4>
                Comentário: A nova alteracao no lexer quebrou o parser. Por favor, reverta o commit para a versao 3.4
                Sua Resposta: "Negativo"
            </exemplo4>
            <exemplo5>
                Comentário: "Entendo a frustração que isso está causando. Vou verificar com a equipe e retornar com uma atualização o mais breve possível."
                Sua Resposta: "Positivo"
            </exemplo5>
        </exemplos>
        <comentários>
            {text}
        </comentários>
    </instruções>
    """
    return prompt


def call_llm(text: str) -> str:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(generate_prompt(text))
    return response.text


def parse_llm_response(response: str) -> str:
    if response.strip().lower() != "positivo" and response.strip().lower() != "negativo":
        return "LLM não conseguiu analisar o sentimento"
    return response


def analyze_sentiments(comments: str) -> str:
    for comment in comments:
        llm_response = call_llm(comment["text"])
        comment["sentiment"] = parse_llm_response(llm_response)


def main():

    analyze_sentiments(github_comments)
    for comment in github_comments:
        print(f"Texto: {comment['text']}")
        print(f"Sentimento: {comment['sentiment']}")
        print("-" * 50)


if __name__ == "__main__":
    main()
