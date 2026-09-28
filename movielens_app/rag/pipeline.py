from db import save_history

from movie_db import get_movie_context

from rag.llm import generate_answer

from rag.vector_store import (
    search_documents
)


# ---------------------------------
# Build final prompt
# ---------------------------------

def build_prompt(
    question: str,
    documents: list[dict],
    sql_context: str
) -> str:

    document_context = "\n\n".join(

        [

            (
                f"[Document chunk {index + 1}]\n"
                f"{item['text']}"
            )

            for index, item
            in enumerate(documents)

        ]

    )


    if not document_context:

        document_context = (
            "No PDF context was found."
        )


    if not sql_context:

        sql_context = (
            "No MovieLens SQL context was found."
        )


    prompt = f"""

You are a MovieLens RAG assistant.

Answer the user's question using
the supplied MovieLens database context
and PDF context.

Rules:

1. Do not invent facts.

2. If the context does not contain
   the answer, clearly say that the
   information was not found in the
   connected data.

3. Prefer exact MovieLens database
   values when they are provided.

4. Keep the answer clear and concise.

5. Do not mention internal implementation
   details unless asked.

MOVIELENS DATABASE CONTEXT:

{sql_context}


PDF CONTEXT:

{document_context}


USER QUESTION:

{question}


ANSWER:

""".strip()


    return prompt


# ---------------------------------
# Complete RAG
# ---------------------------------

def answer_question(
    question: str
):

    # Step 1
    # Search PDF knowledge

    documents = search_documents(
        question,
        n_results=4
    )


    # Step 2
    # Search MovieLens PostgreSQL

    sql_context = get_movie_context(
        question
    )


    # Step 3
    # Build prompt

    prompt = build_prompt(

        question=question,

        documents=documents,

        sql_context=sql_context

    )


    # Step 4
    # Ask local LLM

    answer = generate_answer(
        prompt
    )


    # Step 5
    # Collect PDF sources

    sources = []


    for item in documents:

        source = item[
            "metadata"
        ].get(
            "source"
        )


        if source and source not in sources:

            sources.append(
                source
            )


    # Step 6
    # Save history

    save_history(

        user_prompt=question,

        response=answer,

        sources=sources,

        sql_context=sql_context

    )


    return (
        answer,
        sources,
        documents
    )