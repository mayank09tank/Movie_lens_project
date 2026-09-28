# import fitz
# from rag.vector_store import add_documents


# def chunk_text(text: str, size: int = 500, overlap: int = 50) -> list[str]:
#     chunks, start = [], 0
#     while start < len(text):
#         chunks.append(text[start:start + size])
#         start += size - overlap
#     return [c.strip() for c in chunks if c.strip()]


# def ingest_pdf(pdf_path: str) -> int:
#     doc   = fitz.open(pdf_path)
#     text  = "".join(page.get_text() for page in doc)
#     doc.close()
#     chunks = chunk_text(text)
#     add_documents(chunks, source=pdf_path)
#     return len(chunks)
import pymupdf

from rag.vector_store import add_documents


def chunk_text(
    text: str,
    size: int = 500,
    overlap: int = 50
) -> list[str]:

    if size <= overlap:
        raise ValueError(
            "size must be greater than overlap"
        )

    chunks = []

    start = 0

    step = size - overlap

    while start < len(text):

        chunk = text[start:start + size].strip()

        if chunk:
            chunks.append(chunk)

        start += step

    return chunks


def ingest_pdf(pdf_path: str) -> int:

    with pymupdf.open(pdf_path) as doc:

        pages = [
            page.get_text(
                "text",
                sort=True
            )
            for page in doc
        ]

    text = "\n".join(pages).strip()

    if not text:
        raise ValueError(
            "No text was extracted from this PDF. "
            "It may be a scanned/image-only PDF and needs OCR."
        )

    chunks = chunk_text(text)

    return add_documents(
        chunks,
        source=pdf_path
    )