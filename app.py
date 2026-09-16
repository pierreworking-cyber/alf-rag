import answer
import documents
import question
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
                retrieval_question,
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


if __name__ == "__main__":
    main()
