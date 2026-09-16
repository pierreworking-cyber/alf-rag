import answer
import documents
import retrieve


def choose_document():
    available = documents.available_documents()

    if not available:
        print("No documents found.")
        return None

    print()
    print("Available documents:")
    print()

    for number, path in enumerate(available, start=1):
        print(f"{number}. {path.stem}")

    print()

    while True:
        choice = input(
            f"Select document [1-{len(available)}]: "
        ).strip()

        try:
            number = int(choice)
        except ValueError:
            print("Please enter a number.")
            continue

        if 1 <= number <= len(available):
            return available[number - 1]

        print("Please choose one of the numbers shown.")


def main():
    print()
    print("ALF-RAG")
    print("=======")

    source = choose_document()

    if source is None:
        return

    print()
    print(f"Using: {source.stem}")
    print()
    print("Loading retrieval engine...")

    model = retrieve.load_model()

    print()
    print("Ask a question.")
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

        chunks = retrieve.retrieve(
            question,
            source,
            model,
        )

        evidence = retrieve.build_evidence(
            question,
            chunks,
        )

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
