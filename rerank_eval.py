import json
import time

from pathlib import Path
from sentence_transformers import CrossEncoder


SOURCE = Path("chunks/ebooks/stress/The Difference Engine.json")

MODEL = "cross-encoder/ms-marco-MiniLM-L6-v2"

TOP_K = 5


TESTS = [
    "Who is Sybil Gerard?",
    "Who is Mick Radley?",
    "What role does the man accompanying Sybil play?",
    "Who is the man Sybil is with in the hotel?",
    "What is the relationship between Sybil and Mick?",
    "Why does Sybil trust the man she is with?",
    "Why does she believe he will keep his promise?",
    "Why does she put her faith in him?",
    "What makes her willing to leave everything behind?",
]



def main():
    document = json.loads(
        SOURCE.read_text(encoding="utf-8")
    )

    chunks = document["chunks"]

    print("Loading reranker model...")
    model = CrossEncoder(MODEL)

    for question in TESTS:
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
                }
            )

        results.sort(
            key=lambda result: result["score"],
            reverse=True,
        )

        print()
        print(question)
        print("-" * len(question))

        for result in results[:TOP_K]:
            print(
                f"Chunk {result['id']:3} "
                f"score={result['score']:.4f}"
            )

    start = time.perf_counter()

    scores = model.predict(pairs)

    elapsed = time.perf_counter() - start

    print(
        f"Scored {len(pairs)} chunks in {elapsed:.2f} seconds"
    )

if __name__ == "__main__":
    main()
