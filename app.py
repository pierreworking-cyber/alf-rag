import retrieve
import answer


def main():
    print()
    print("ALF-RAG")
    print("=======")
    print("Ask a question about The Difference Engine.")
    print("Type 'quit' or 'exit' to leave.")
    print()

    while True:
        question = input("> ").strip()

        if not question:
            continue

        if question.lower() in {"quit", "exit"}:
            print("Goodbye.")
            break

        print()
        print("Retrieving evidence...")

        chunks = retrieve.retrieve(question)

        evidence_parts = [
            f"Question: {question}",
            "Retrieved evidence:",
        ]

        for chunk in chunks:
            evidence_parts.append(
                f"\n--- Chunk {chunk['id']} ---\n"
                f"{chunk['text']}"
            )

        evidence = "\n".join(evidence_parts)

        print("Generating answer...")
        print()

        try:
            response = answer.answer(
                question,
                evidence,
            )
        except RuntimeError as error:
            print(error)
            print()
            continue

        print(response)
        print()

        chunk_ids = [
            str(chunk["id"])
            for chunk in chunks
        ]

        print(
            "Sources: "
            + ", ".join(chunk_ids)
        )
        print()


if __name__ == "__main__":
    main()
