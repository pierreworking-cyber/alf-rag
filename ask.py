import re
import subprocess
from pathlib import Path


QUESTIONS = Path("test_questions.txt")
EVIDENCE = Path("retrieved_evidence.txt")
RESULTS = Path("test_results")


def main():
    questions = [
        line.strip()
        for line in QUESTIONS.read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    ]

    RESULTS.mkdir(exist_ok=True)

    for number, question in enumerate(questions, start=1):
        print()
        print("=" * 70)
        print(f"QUESTION {number}/{len(questions)}")
        print("=" * 70)
        print(question)
        print()

        # --------------------------------------------------------
        # Retrieve evidence
        # --------------------------------------------------------

        retrieve = subprocess.run(
            [
                "python",
                "retrieve.py",
                question,
            ],
            text=True,
            capture_output=True,
        )

        if retrieve.returncode != 0:
            print("RETRIEVAL FAILED")
            print(retrieve.stderr)
            continue

        evidence = EVIDENCE.read_text(
            encoding="utf-8"
        )

        chunks = re.findall(
            r"--- Chunk (\d+) ---",
            evidence,
        )

        chunk_list = ", ".join(chunks)

        # --------------------------------------------------------
        # Generate answer
        # --------------------------------------------------------

        answer = subprocess.run(
            [
                "python",
                "answer.py",
            ],
            text=True,
            capture_output=True,
        )

        if answer.returncode != 0:
            print("ANSWER GENERATION FAILED")
            print(answer.stderr)
            continue

        # --------------------------------------------------------
        # Save raw answer output
        # --------------------------------------------------------

        output_file = RESULTS / f"{number:02d}.txt"

        output_file.write_text(
            answer.stdout,
            encoding="utf-8",
        )

        # --------------------------------------------------------
        # Display concise result
        # --------------------------------------------------------

        output = answer.stdout.strip()

        if "...done thinking." in output:
            output = output.split(
                "...done thinking.",
                1,
            )[1].strip()

        print("ANSWER")
        print("------")
        print(output)

        print()
        print(f"CHUNKS")
        print("------")
        print(chunk_list)


if __name__ == "__main__":
    main()
