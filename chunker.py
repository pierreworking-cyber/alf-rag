import json
from pathlib import Path

from docling.document_converter import DocumentConverter


SOURCE = Path("documents/ebooks/stress/The Difference Engine.epub")
OUTPUT = Path("chunks/ebooks/stress/The Difference Engine.json")

MAX_WORDS = 500


def main():
    converter = DocumentConverter()
    result = converter.convert(SOURCE)

    document = result.document

    chunks = []
    current_items = []
    current_words = 0

    for item in document.texts:
        text = item.text.strip()

        if not text:
            continue

        words = len(text.split())

        if current_items and current_words + words > MAX_WORDS:
            chunks.append({
                "id": len(chunks) + 1,
                "text": "\n\n".join(current_items),
            })

            current_items = []
            current_words = 0

        current_items.append(text)
        current_words += words

    if current_items:
        chunks.append({
            "id": len(chunks) + 1,
            "text": "\n\n".join(current_items),
        })

    output = {
        "document": {
            "name": document.name,
            "source_file": SOURCE.name,
            "format": SOURCE.suffix.lstrip("."),
        },
        "chunks": chunks,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    OUTPUT.write_text(
        json.dumps(output, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"Created {OUTPUT}")
    print(f"Chunks: {len(chunks)}")


if __name__ == "__main__":
    main()
