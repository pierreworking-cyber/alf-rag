import json
import sys
from pathlib import Path

import documents
from sentence_transformers import CrossEncoder

from sentence_transformers import CrossEncoder

MODEL = "cross-encoder/ms-marco-MiniLM-L6-v2"
DEFAULT_SOURCE = Path(
    "chunks/ebooks/stress/The Difference Engine.json"
)

TOP_K = 5

def load_model():
    import logging

    from transformers.utils import logging as transformers_logging

    transformers_logging.disable_progress_bar()
    transformers_logging.set_verbosity_error()

    logging.getLogger("huggingface_hub").setLevel(
        logging.ERROR
    )

    return CrossEncoder(MODEL)

def retrieve(question, source, model):
    chunk_file = documents.chunk_path(source)

    document = json.loads(
        chunk_file.read_text(encoding="utf-8")
    )

    chunks = document["chunks"]

    # ------------------------------------------------------------
    # Semantic retrieval
    # ------------------------------------------------------------


    pairs = [
        [question, chunk["text"]]
        for chunk in chunks
    ]

    scores = model.predict(pairs)

    results = []

    for chunk, score in zip(chunks, scores):
        results.append(
            {
                "id": chunk["id"],
                "score": float(score),
                "text": chunk["text"],
            }
        )

    results.sort(
        key=lambda result: result["score"],
        reverse=True,
    )

    # ------------------------------------------------------------
    # Select evidence
    # ------------------------------------------------------------

    selected_ids = {
        result["id"]
        for result in results[:TOP_K]
    }

    # Chunk 1 remains deliberately included.
    selected_ids.add(1)

    selected = [
        chunk
        for chunk in chunks
        if chunk["id"] in selected_ids
    ]

    return selected

def build_evidence(question, chunks):
    evidence_parts = [
        f"Question: {question}",
        "Retrieved evidence:",
    ]

    for chunk in chunks:
        evidence_parts.append(
            f"\n--- Chunk {chunk['id']} ---\n"
            f"{chunk['text']}"
        )

    return "\n".join(evidence_parts)


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print('  python retrieve.py "your question here"')
        sys.exit(1)

    question = " ".join(sys.argv[1:])

    selected = retrieve(
            question,
            DEFAULT_SOURCE,
            model,)

    # ------------------------------------------------------------
    # Write evidence for the next stage
    # ------------------------------------------------------------

    evidence_parts = []

    evidence_parts.append(
        f"Question: {question}"
    )

    evidence_parts.append(
        "Retrieved evidence:"
    )

    for chunk in selected:
        evidence_parts.append(
            f"\n--- Chunk {chunk['id']} ---\n"
            f"{chunk['text']}"
        )

    evidence = "\n".join(evidence_parts)

    Path("retrieved_evidence.txt").write_text(
        evidence,
        encoding="utf-8",
    )

    # ------------------------------------------------------------
    # Display summary
    # ------------------------------------------------------------

    print()
    print(f"Question: {question}")
    print()
    print("SELECTED CHUNKS")
    print("---------------")

    for chunk in selected:
        print(f"Chunk {chunk['id']}")

    print()
    print("Evidence written to retrieved_evidence.txt")


if __name__ == "__main__":
    main()
