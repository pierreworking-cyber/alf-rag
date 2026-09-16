from pathlib import Path


CHUNKS_ROOT = Path("chunks")


def available_documents():
    documents = []

    for path in CHUNKS_ROOT.rglob("*.json"):
        documents.append(path)

    return sorted(documents)
