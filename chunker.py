import json
from pathlib import Path

from docling.document_converter import DocumentConverter


DOCUMENTS_ROOT = Path("documents")
CHUNKS_ROOT = Path("chunks")

MAX_WORDS = 500


def chunk_document(document):
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

    return chunks


def chunk_path(source):
    relative = source.relative_to(DOCUMENTS_ROOT)

    return (
        CHUNKS_ROOT
        / relative.parent
        / f"{source.stem}.json"
    )


def process_document(source):
    source = Path(source)




    if source.suffix.lower() == ".pdf":
        from docling.datamodel.pipeline_options import PdfPipelineOptions
        from docling.document_converter import PdfFormatOption

        pipeline_options = PdfPipelineOptions(
            do_ocr=False,
            force_backend_text=True,
        )

        converter = DocumentConverter(
            format_options={
                "pdf": PdfFormatOption(
                    pipeline_options=pipeline_options,
                )
            }
        )
    else:
        converter = DocumentConverter()




    result = converter.convert(source)

    document = result.document
    chunks = chunk_document(document)

    output = {
        "document": {
            "name": document.name,
            "source_file": source.name,
            "format": source.suffix.lstrip(".").lower(),
        },
        "chunks": chunks,
    }

    output_path = chunk_path(source)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        json.dumps(
            output,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return output_path, len(chunks)
