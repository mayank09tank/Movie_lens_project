# import chromadb
# from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

# _client = chromadb.PersistentClient(path="./chroma_db")
# _ef     = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
# _col    = _client.get_or_create_collection("movielens_docs", embedding_function=_ef)


# def add_documents(chunks: list[str], source: str):
#     ids = [f"{source}_{i}" for i in range(len(chunks))]
#     _col.upsert(documents=chunks, ids=ids, metadatas=[{"source": source}] * len(chunks))


# def query(question: str, top_k: int = 3) -> list[str]:
#     results = _col.query(query_texts=[question], n_results=top_k)
#     return results["documents"][0] if results["documents"] else []

import os
import hashlib
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer


load_dotenv()


CHROMA_DIR = os.getenv(
    "CHROMA_DIR",
    "./chroma_db"
)

COLLECTION_NAME = os.getenv(
    "CHROMA_COLLECTION",
    "movie_documents"
)

EMBEDDING_MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL",
    "all-MiniLM-L6-v2"
)


Path(CHROMA_DIR).mkdir(
    parents=True,
    exist_ok=True
)


# -----------------------------
# Create ChromaDB client
# -----------------------------

client = chromadb.PersistentClient(
    path=CHROMA_DIR
)


# -----------------------------
# Create / get collection
# -----------------------------

collection = client.get_or_create_collection(
    name=COLLECTION_NAME
)


# -----------------------------
# Load embedding model
# -----------------------------

embedding_model = SentenceTransformer(
    EMBEDDING_MODEL_NAME
)


# -----------------------------
# Create unique ID
# -----------------------------

def _make_id(
    source: str,
    index: int
) -> str:

    raw = f"{source}|{index}".encode(
        "utf-8"
    )

    return hashlib.sha1(
        raw
    ).hexdigest()


# -----------------------------
# Add documents
# -----------------------------

def add_documents(
    chunks: list[str],
    source: str
) -> int:

    if not chunks:
        return 0

    ids = []

    documents = []

    metadatas = []


    for index, chunk in enumerate(chunks):

        ids.append(
            _make_id(
                source,
                index
            )
        )

        documents.append(chunk)

        metadatas.append(
            {
                "source": str(source),
                "chunk_index": index
            }
        )


    # -------------------------
    # Create embeddings
    # -------------------------

    embeddings = embedding_model.encode(
        documents,
        normalize_embeddings=True
    ).tolist()


    # -------------------------
    # Store in ChromaDB
    # -------------------------

    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )


    return len(documents)


# -----------------------------
# Search documents
# -----------------------------

def search_documents(
    query: str,
    n_results: int = 4
) -> list[dict]:

    total = collection.count()


    if total == 0:
        return []


    # Convert question into vector

    query_embedding = embedding_model.encode(
        [query],
        normalize_embeddings=True
    ).tolist()


    # Search ChromaDB

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=min(
            n_results,
            total
        ),
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )


    documents = results.get(
        "documents",
        [[]]
    )[0]

    metadatas = results.get(
        "metadatas",
        [[]]
    )[0]

    distances = results.get(
        "distances",
        [[]]
    )[0]


    output = []


    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances
    ):

        output.append(
            {
                "text": document,
                "metadata": metadata,
                "distance": distance
            }
        )


    return output


# -----------------------------
# Number of stored chunks
# -----------------------------

def collection_count() -> int:

    return collection.count()