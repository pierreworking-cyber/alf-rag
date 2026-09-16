import subprocess
from pathlib import Path


MODEL = "gemma4:31b-cloud"


def answer(question, evidence):
    prompt = f"""
You are answering a question about a book.

Use ONLY the supplied evidence to answer the question.

Do not use outside knowledge.
Do not invent facts that are not supported by the evidence.

If the evidence is insufficient to answer the question,
say that the evidence is insufficient.

When interpreting the evidence, distinguish between:

- events and scenes that are part of the book's main narrative;
- historical events mentioned or quoted within the narrative;
- dates belonging to quoted books, documents, or other source material;
- publication dates or copyright information;
- descriptions of settings or imagined scenes that may not be part
  of the main narrative.

Do not automatically treat every date mentioned in the evidence as
a date in the story's main narrative.

If the question asks about the time span or chronology of the story,
identify the dates associated with the main narrative rather than
simply giving the earliest and latest dates mentioned anywhere in
the supplied text.

If the question asks what happened, identify actual events or actions.
Do not substitute a description of a place, person, or setting for
an event.

Give a concise, natural answer.

Here is the question and retrieved evidence:

{evidence}
"""

    result = subprocess.run(
        [
            "ollama",
            "run",
            MODEL,
        ],
        input=prompt,
        text=True,
        capture_output=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Ollama failed:\n{result.stderr}"
        )

    output = result.stdout.strip()

    if "...done thinking." in output:
        output = output.split(
            "...done thinking.",
            1,
        )[1].strip()

    return output


def main():
    evidence_file = Path("retrieved_evidence.txt")

    if not evidence_file.exists():
        print(
            "No retrieved evidence found. "
            "Run retrieve.py first."
        )
        return

    evidence = evidence_file.read_text(
        encoding="utf-8"
    )

    question = evidence.split(
        "Retrieved evidence:",
        1,
    )[0].strip()

    print("Asking LLM...")
    print()

    print(
        answer(
            question,
            evidence,
        )
    )


if __name__ == "__main__":
    main()
