import answer
import chunker
import documents
import question
import retrieve


def choose_processed_document():
    available = [
        path
        for path in documents.available_documents()
        if documents.is_processed(path)
    ]

    if not available:
        print()
        print("No processed books available.")
        print("Process a book first.")
        print()
        return None

    print()
    print("Available books:")
    print()

    for number, path in enumerate(available, start=1):
        print(f"{number}. {path.stem}")

    print()

    while True:
        choice = input(
            f"Select [1-{len(available)}]: "
        ).strip()

        if choice.lower() in {"quit", "exit"}:
            return None

        try:
            number = int(choice)
        except ValueError:
            print("Please enter a number.")
            continue

        if 1 <= number <= len(available):
            return available[number - 1]

        print("Please choose one of the numbers shown.")


def choose_new_document():
    available = [
        path
        for path in documents.available_documents()
        if not documents.is_processed(path)
    ]

    if not available:
        print()
        print("No new books to process.")
        print()
        return None

    print()
    print("Available new books:")
    print()

    for number, path in enumerate(available, start=1):
        print(f"{number}. {path.stem}")

    print()

    while True:
        choice = input(
            f"Select [1-{len(available)}]: "
        ).strip()

        if choice.lower() in {"quit", "exit"}:
            return None
        try:
            number = int(choice)
        except ValueError:
            print("Please enter a number.")
            continue

        if 1 <= number <= len(available):
            return available[number - 1]

        print("Please choose one of the numbers shown.")


def process_book():
    source = choose_new_document()

    if source is None:
        return

    print()
    print(f"Processing: {source.stem}")
    print()

    _, chunk_count = chunker.process_document(source)

    print("Processing complete.")
    print(f"Created {chunk_count} chunks.")
    print()



def discuss_book():
    source = choose_processed_document()

    if source is None:
        return

    print()
    print(f"Using: {source.stem}")
    print("Context: OFF")
    print()
    print("Loading retrieval engine...")

    model = retrieve.load_model()

    context_enabled = False
    conversation = []

    print()
    print("Ask a question.")
    print("Type '/context' to toggle conversation mode.")
    print("Type 'quit' or 'exit' to leave.")
    print()

    while True:
        question_text = input("> ").strip()

        if not question_text:
            continue

        if question_text.lower() in {"quit", "exit"}:
            print("Goodbye.")
            break

        if question_text.lower() == "/context":
            context_enabled = not context_enabled

            state = "ON" if context_enabled else "OFF"

            print()
            print(f"Context: {state}")
            print()

            continue

        retrieval_question = question_text

        if context_enabled:
            try:
                retrieval_question = question.resolve(
                    question_text,
                    conversation,
                    source.stem,
                )
            except RuntimeError as error:
                print(error)
                print()
                continue

        if retrieval_question != question_text:
            print()
            print(
                f"Interpreted as: {retrieval_question}"
            )

        print()
        print("Retrieving evidence...")

        chunks = retrieve.retrieve(
            retrieval_question,
            source,
            model,
        )

        evidence = retrieve.build_evidence(
            retrieval_question,
            chunks,
        )

        print("Generating answer...")
        print()

        try:
            response = answer.answer(
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

        if context_enabled:
            conversation.append(
                {
                    "question": question_text,
                    "answer": response,
                }
            )


def main():
    print()
    print("ALF-RAG")
    print("=======")

    while True:
        print()
        print("Books")
        print()

        print("1. Process a new book")
        print("2. Discuss a book")
        print("3. Quit")
        print()

        choice = input("Select [1-3]: ").strip()

        if choice == "1":
            process_book()

        elif choice == "2":
            discuss_book()

        elif choice == "3":
            print()
            print("Goodbye.")
            return

        else:
            print()
            print("Please choose one of the numbers shown.")
            print()


if __name__ == "__main__":
    main()
