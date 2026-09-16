import json
from pathlib import Path


SOURCE = Path("markdown/ebooks/stress/The Difference Engine.md")
OUTPUT = Path("chunks/ebooks/stress/The Difference Engine.json")

MAX_WORDS = 500


def main():
    markdown = SOURCE.read_text(encoding="utf-8")

    paragraphs = [
        paragraph.strip()
        for paragraph in markdown.split("\n\n")
        if paragraph.strip()
    ]

    chunks = []
    current_paragraphs = []
    current_words = 0

    for paragraph in paragraphs:
        paragraph_words = len(paragraph.split())

        if current_paragraphs and current_words + paragraph_words > MAX_WORDS:
            chunks.append({
                "id": len(chunks) + 1,
                "text": "\n\n".join(current_paragraphs),
            })

            current_paragraphs = []
            current_words = 0

        current_paragraphs.append(paragraph)
        current_words += paragraph_words

    if current_paragraphs:
        chunks.append({
            "id": len(chunks) + 1,
            "text": "\n\n".join(current_paragraphs),
        })

    document = {
        "document": {
            "title": "The Difference Engine",
            "author": "William Gibson",
            "source_file": "The Difference Engine.epub",
            "format": "epub",
        },
        "chunks": chunks,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    OUTPUT.write_text(
        json.dumps(document, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
