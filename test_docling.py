from docling.document_converter import DocumentConverter


source = "documents/ebooks/stress/The Difference Engine.epub"

converter = DocumentConverter()

result = converter.convert(source)

document = result.document

print("DOCUMENT")
print("========")
print(f"Name:  {document.name}")
print(f"Pages: {len(document.pages)}")
print()

print("FIRST TEXT ITEM")
print("================")

item = document.texts[0]

print(f"Type: {type(item).__name__}")
print()

print("ATTRIBUTES")
print("----------")

for name in dir(item):
    if name.startswith("_"):
        continue

    try:
        value = getattr(item, name)

        if callable(value):
            continue

        print(f"{name}: {value!r}")

    except Exception:
        pass
