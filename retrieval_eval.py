import json
from pathlib import Path

from rank_bm25 import BM25Okapi


SOURCE = Path("chunks/ebooks/stress/The Difference Engine.json")

CANDIDATE_SIZES = [30, 50, 100, 150]


TESTS = [
    {
        "question": "Who is Sybil Gerard?",
        "relevant": [1],
    },
    {
        "question": "Who is Mick Radley?",
        "relevant": [1, 5],
    },
    {
        "question": "What role does the man accompanying Sybil play?",
        "relevant": [41, 72, 76, 77],
    },
    {
        "question": "Who is the man Sybil is with in the hotel?",
        "relevant": [1, 5, 9, 12],
    },
    {
        "question": "What is the relationship between Sybil and Mick?",
        "relevant": [11, 22, 41, 53],
    },
    {
        "question": "Why does Sybil trust the man she is with?",
        "relevant": [5, 7],
    },
    {
        "question": "Why does she believe he will keep his promise?",
        "relevant": [7],
    },
    {
        "question": "Why does she put her faith in him?",
        "relevant": [7, 47],
    },
    {
        "question": "What makes her willing to leave everything behind?",
        "relevant": [7, 40],
    },
]


def tokenize(text):
    return text.lower().split()


def main():
    document = json.loads(
        SOURCE.read_text(encoding="utf-8")
    )

    chunks = document["chunks"]

    tokenized_chunks = [
        tokenize(chunk["text"])
        for chunk in chunks
    ]

    bm25 = BM25Okapi(tokenized_chunks)

    print()
    print("BM25 CANDIDATE RECALL")
    print("=====================")
    print()

    for test in TESTS:
        question = test["question"]
        relevant = set(test["relevant"])

        query_tokens = tokenize(question)

        scores = bm25.get_scores(query_tokens)

        ranked = sorted(
            zip(chunks, scores),
            key=lambda item: item[1],
            reverse=True,
        )

        print(question)
        print("-" * len(question))

        for size in CANDIDATE_SIZES:
            candidates = ranked[:size]

            candidate_ids = {
                chunk["id"]
                for chunk, _ in candidates
            }

            found = relevant & candidate_ids

            print(
                f"K={size:3}: "
                f"{len(found)}/{len(relevant)} relevant chunks found "
                f"{sorted(found)}"
            )

        print()


if __name__ == "__main__":
    main()
