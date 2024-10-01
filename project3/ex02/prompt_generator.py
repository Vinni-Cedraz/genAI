#!/usr/bin/env python3.10
import google.generativeai as genai
from dotenv import load_dotenv
import os


load_dotenv()


def create_prompt(role: str, task: str, topic: str, specific_question: str) -> str:
    xml_prompt_pt_br = f"""
    Follow the instructions detailed for you in the instructions below, the text within the xml tags is for your own instruction and shouldn't be present in your response:
    <instructions>
        <role>{role}</role>
        <task>{task}</task>
        <topic>{topic}</topic>
        <specificQuestion>{specific_question}</specificQuestion>
        <topicsExpectedInTheAnswer>
            * Explicação básica do conceito
            * Uma analogia tirada da vida cotidiana comum da pessoa média
            * Resposta com explicação passo a passo
            * Dois exemplos detalhados
            * Uma dica prática para lembrar a ideia geral, para leigos
        </topicsExpectedInTheAnswer>
        <example>
            <title> René Descartes </title>
            <1>
                René Descartes foi um filósofo e matemático francês do século XVII considerado o pai da filosofia moderna.
                Ele buscava um fundamento sólido para o conhecimento em uma época marcada por incertezas. Sua frase
                mais famosa, "Penso, logo existo", resume sua ideia central: a única certeza que temos é a de nossa
                própria existência, pois duvidar dela já comprova que pensamos, e portanto, existimos.
            </1>
            <2>
                Imagine que você está sonhando. No sonho, tudo parece real, mas ao acordar você percebe que não era.
                Descartes se perguntou como ter certeza de que não estamos vivendo em um sonho constante. A única
                certeza que encontrou foi o próprio ato de duvidar, de pensar, pois isso indicava a existência de um
                "eu" que duvida.
            </2>
            <3>
                **Quem foi René Descartes?** Um filósofo e matemático que buscava a verdade e a incerteza.
                **O que ele buscava?** Um fundamento sólido para o conhecimento, algo que fosse irrefutavelmente verdadeiro.
                **Como ele chegou à frase?** Duvidando de tudo, inclusive do mundo externo e do próprio corpo.
                **Qual a conclusão?** A única certeza é que, ao duvidar de tudo, ele estava pensando, e que se estava pensando, então existia.
            </3>
            <4>
                    <exemplo1>
                        Imagine que você se depara com uma ilusão de ótica ou uma miragem, os seus olhos
                        veem uma coisa, mas você sabe que é uma ilusão, que a realidade
                        é diferente. Descartes aplica essa ideia ao conhecimento em
                        geral: como saber se o que percebemos é real ou ilusório? Para
                        ele, a única certeza é o ato de duvidar e questionar, pois isso
                        implica um sujeito pensante.
                    </exemplo1>
                    <exemplo2>
                        Image que você questiona a existência do mundo exterior ou do próprio corpo. No entanto, percebe que a dúvida em si é uma forma de pensamento. Se você está pensando, então você existe. Isso é o que Descartes quer dizer com "Cogito, ergo sum" - "Penso, logo existo".
                    </exemplo2>
            </4>
            <5>
                Lembre-se da frase "Penso, logo existo" quando se deparar com
                informações complexas ou questionamentos sobre a realidade. Ela nos
                lembra que a capacidade de pensar criticamente e questionar é
                fundamental para a busca da verdade.
            </5>
        </example>
    </instructions>"""
    return xml_prompt_pt_br


def send_to_gemini(instructions: str) -> str:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(instructions)
    return response.text


def main():

    test_examples = [
        {
            "role": "assistente especializado em ensinar programação Python para iniciantes",
            "task": "explicar conceitos básicos de Python e fornecer exemplos simples e práticos",
            "topic": "list comprehensions em Python",
            "specific_question": "O que é uma list comprehension e como posso usá-la para criar uma lista de números pares de 0 a 10?",
        },
        {
            "role": "especialista em métodos de educação inovadores em tecnologia",
            "task": "explicar o conceito e a abordagem única da École 42 para interessados em educação em tecnologia",
            "topic": "École 42 e seu método de ensino",
            "specific_question": "O que é a École 42 e como seu método de ensino difere das faculdades tradicionais de computação?",
        },
        {
            "role": "historiador da ciência da computação e teoria da informação",
            "task": "explicar a importância de Claude Shannon e suas contribuições para iniciantes em ciência da computação",
            "topic": "Claude Shannon e a Teoria da Informação",
            "specific_question": "Quem foi Claude Shannon e qual foi sua principal contribuição para a ciência da computação e comunicação?",
        },
        {
            "task": "explicar o pensamento de Descartes e sua influência para iniciantes em filosofia",
            "role": "especialista em filosofia e história da ciência",
            "topic": "René Descartes e o Método Cartesiano",
            "specific_question": "Quem foi René Descartes e qual é o significado da frase 'Penso, logo existo'?",
        },
    ]

    for example in test_examples:
        role = example["role"]
        task = example["task"]
        topic = example["topic"]
        specific_question = example["specific_question"]
        instructions = create_prompt(role, task, topic, specific_question)
        response = send_to_gemini(instructions)
        print("\nResposta do Gemini 1.5 Flash:")
        print(response)

    instructions = create_prompt(role, task, topic, specific_question)
    response = send_to_gemini(instructions)
    print("\nResposta do Gemini 1.5 Flash:")
    print(response)


if __name__ == "__main__":
    main()
