import json
from pathlib import Path

from sentence_transformers import CrossEncoder


SOURCE = Path("chunks/ebooks/stress/The Difference Engine.json")

MODEL = "cross-encoder/ms-marco-MiniLM-L6-v2"

TOP_K = 10


def main():
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print('  python rerank_test.py "your question here"')
        sys.exit(1)

    question = " ".join(sys.argv[1:])

    document = json.loads(
        SOURCE.read_text(encoding="utf-8")
    )

    chunks = document["chunks"]

    print("Loading model...")
    model = CrossEncoder(MODEL)

    pairs = [
        [question, chunk["text"]]
        for chunk in chunks
    ]

    print("Scoring chunks...")

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

    print()
    print(f"Question: {question}")
    print()
    print("TOP RERANKED CHUNKS")
    print("-------------------")

    for result in results[:TOP_K]:
        print()
        print(f"Chunk {result['id']}")
        print(f"Score: {result['score']:.4f}")
        print("-" * 40)
        print(result["text"])

if __name__ == "__main__":
    main()
