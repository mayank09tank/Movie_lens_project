# import ollama


# def ask(question: str, context_chunks: list[str]) -> str:
#     context  = "\n\n".join(context_chunks)
#     prompt   = f"""You are a helpful assistant. Use the context below to answer the question.
# If the answer is not in the context, say "I don't have enough information."

# Context:
# {context}

# Question: {question}
# Answer:"""
#     response = ollama.chat(
#         model="llama3",
#         messages=[{"role": "user", "content": prompt}]
#     )
#     return response["message"]["content"]


import os

import requests
from dotenv import load_dotenv


load_dotenv()


OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434/api/generate"
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "llama3.2:3b"
)


def generate_answer(
    prompt: str
) -> str:

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }


    try:

        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=120
        )

        response.raise_for_status()


    except requests.RequestException as exc:

        raise RuntimeError(
            "Could not connect to Ollama. "
            "Make sure Ollama is running "
            "and the model is installed."
        ) from exc


    data = response.json()


    if "response" not in data:

        raise RuntimeError(
            f"Unexpected Ollama response: {data}"
        )


    return data["response"].strip()