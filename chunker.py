import json
import re
from pathlib import Path

from docling.document_converter import DocumentConverter


DOCUMENTS_ROOT = Path("documents")
CHUNKS_ROOT = Path("chunks")

MAX_WORDS = 500


def chunk_document(document):
    chunks = []
    structure = []

    section_headers = [
        item.text.strip()
        for item in document.texts
        if str(getattr(item, "label", "")) == "section_header"
        and item.text.strip()
    ]

    has_parts = any(
        text.startswith("Part ")
        for text in section_headers
    )

    current_items = []
    current_words = 0
    current_structure = None
    structure_started = False

    for item in document.texts:
        text = item.text.strip()

        if not text:
            continue

        is_section_header = (
            str(getattr(item, "label", "")) == "section_header"
        )

        is_part = (
            is_section_header
            and text.startswith("Part ")
        )

        is_major_heading = (
            is_section_header
            and (
                text.startswith("Chapter ")
                or text.startswith("Appendix ")
            )
        )

        is_numbered_section = (
            is_section_header
            and bool(
                re.match(
                    r"^[IVXLCDM]+\s+\ue000\s+",
                    text,
                )
            )
        )

        if has_parts:
            if is_part:
                structure_started = True
        elif is_part or is_major_heading or is_numbered_section:
            structure_started = True

        if structure_started and (
            is_part
            or is_major_heading
            or is_numbered_section
        ):
            if current_items:
                chunks.append({
                    "id": len(chunks) + 1,
                    "text": "\n\n".join(current_items),
                })

                current_items = []
                current_words = 0

            if current_structure is not None:
                current_structure["end_chunk"] = len(chunks)

            if is_part:
                structure_type = "part"
            elif text.startswith("Chapter "):
                structure_type = "chapter"
            elif text.startswith("Appendix "):
                structure_type = "appendix"
            else:
                structure_type = "section"

            current_structure = {
                "type": structure_type,
                "title": text,
                "start_chunk": len(chunks) + 1,
                "sections": [],
            }

            structure.append(current_structure)

        elif structure_started and is_section_header:
            if current_structure is not None:
                current_structure["sections"].append({
                    "title": text,
                    "start_chunk": len(chunks) + 1,
                })

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

    if current_structure is not None:
        current_structure["end_chunk"] = len(chunks)

    return chunks, structure

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
    chunks, structure = chunk_document(document)

    output = {
        "document": {
            "name": document.name,
            "source_file": source.name,
            "format": source.suffix.lstrip(".").lower(),
        },
        "structure": structure,
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
