from pathlib import Path


DOCUMENTS_ROOT = Path("documents")
CHUNKS_ROOT = Path("chunks")


def available_documents():
    documents = []

    for path in DOCUMENTS_ROOT.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".epub", ".pdf"}:
            documents.append(path)

    return sorted(documents)


def chunk_path(document):
    relative = document.relative_to(DOCUMENTS_ROOT)

    return (
        CHUNKS_ROOT
        / relative.parent
        / f"{document.stem}.json"
    )


def is_processed(document):
    return chunk_path(document).exists()
