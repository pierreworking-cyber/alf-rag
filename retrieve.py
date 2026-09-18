import json
import sys
from pathlib import Path

import documents
from sentence_transformers import CrossEncoder

MODEL = "cross-encoder/ms-marco-MiniLM-L6-v2"

TOP_K = 5
CONTEXT_RADIUS = 2

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
    # Display retrieval ranking
    # ------------------------------------------------------------

    print()
    print("RETRIEVAL RANKING")
    print("-----------------")

    for rank, result in enumerate(results[:10], start=1):
        print(
            f"{rank:2}. Chunk {result['id']:>3} "
            f"score={result['score']:.4f}"
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

    selected = expand_context(
        chunks,
        document["structure"],
        selected_ids,
    )

    return selected

def structure_for_chunk(structure, chunk_id):
    for entry in structure:
        if entry["start_chunk"] <= chunk_id <= entry["end_chunk"]:
            return entry

    return None


def expand_context(chunks, structure, selected_ids):
    chunk_by_id = {
        chunk["id"]: chunk
        for chunk in chunks
    }

    expanded_ids = set(selected_ids)

    for chunk_id in selected_ids:
        entry = structure_for_chunk(
            structure,
            chunk_id,
        )

        if entry is None:
            continue

        start = max(
            entry["start_chunk"],
            chunk_id - CONTEXT_RADIUS,
        )

        end = min(
            entry["end_chunk"],
            chunk_id + CONTEXT_RADIUS,
        )

        expanded_ids.update(
            range(start, end + 1)
        )

    return [
        chunk_by_id[chunk_id]
        for chunk_id in sorted(expanded_ids)
    ]


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

    model = load_model()

    selected = retrieve(
        question,
        DEFAULT_SOURCE,
        model,
    )

    evidence = build_evidence(
        question,
        selected,
    )

    Path("retrieved_evidence.txt").write_text(
        evidence,
        encoding="utf-8",
    )

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
