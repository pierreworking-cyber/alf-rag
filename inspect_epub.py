import sys
from collections import Counter
from pathlib import Path
import xml.etree.ElementTree as ET

from ebooklib import epub, ITEM_DOCUMENT


def local_name(tag):
    """Return an XML tag without its namespace."""
    return tag.rsplit("}", 1)[-1]


def inspect_document(item):
    content = item.get_content()

    try:
        root = ET.fromstring(content)
    except ET.ParseError as error:
        print(f"Could not parse XML: {error}")
        return

    elements = list(root.iter())

    print()
    print(item.get_name())
    print("-" * len(item.get_name()))

    print(f"Size: {len(content):,} bytes")
    print(f"Elements: {len(elements):,}")
    print()

    # ------------------------------------------------------------
    # Element counts
    # ------------------------------------------------------------

    element_counts = Counter(
        local_name(element.tag)
        for element in elements
    )

    print("ELEMENTS")
    print("--------")

    for tag, count in element_counts.most_common():
        print(f"{tag:<12} {count:>6}")

    print()

    # ------------------------------------------------------------
    # CSS classes
    # ------------------------------------------------------------

    classes = Counter()

    for element in elements:
        class_name = element.attrib.get("class")

        if class_name:
            classes[class_name] += 1

    print("CSS CLASSES")
    print("-----------")

    if classes:
        for class_name, count in classes.most_common():
            print(f"{class_name:<30} {count:>6}")
    else:
        print("(none)")

    print()

    # ------------------------------------------------------------
    # EPUB-specific attributes
    # ------------------------------------------------------------

    epub_attributes = Counter()

    for element in elements:
        for attribute in element.attrib:
            if "idpf.org/2007/ops" in attribute:
                epub_attributes[attribute] += 1

    print("EPUB ATTRIBUTES")
    print("---------------")

    if epub_attributes:
        for attribute, count in epub_attributes.most_common():
            print(f"{attribute:<50} {count:>6}")
    else:
        print("(none)")

    print()

    # ------------------------------------------------------------
    # First 20 text-bearing elements
    # ------------------------------------------------------------

    print("FIRST 20 TEXT ELEMENTS")
    print("----------------------")

    shown = 0

    for element in elements:
        text = "".join(element.itertext()).strip()

        if not text:
            continue

        tag = local_name(element.tag)

        # Ignore html/body/head etc. unless they actually contain
        # a useful text block.
        if tag in {"html", "body", "head", "title"}:
            continue

        text = " ".join(text.split())

        print(f"{shown + 1:>2}. <{tag}> {text[:160]}")

        shown += 1

        if shown >= 20:
            break


def main():
    if len(sys.argv) != 2:
        print("Usage:")
        print("  python inspect_epub.py <ebook.epub>")
        sys.exit(1)

    source = Path(sys.argv[1])

    if not source.exists():
        print(f"File not found: {source}")
        sys.exit(1)

    book = epub.read_epub(source)

    print("EPUB INSPECTION")
    print("===============")
    print(f"File: {source}")
    print()

    print("METADATA")
    print("========")

    print(f"Title:    {book.get_metadata('DC', 'title')}")
    print(f"Creator:  {book.get_metadata('DC', 'creator')}")
    print(f"Date:     {book.get_metadata('DC', 'date')}")
    print(f"Language: {book.get_metadata('DC', 'language')}")
    print(f"Publisher:{book.get_metadata('DC', 'publisher')}")
    print()

    print("SPINE")
    print("=====")

    for item_id, _ in book.spine:
        item = book.get_item_with_id(item_id)
        print(f"{item_id}: {item.get_name()}")

    print()

    print("TABLE OF CONTENTS")
    print("=================")

    for entry in book.toc:
        if isinstance(entry, epub.Link):
            print(f"{entry.title} -> {entry.href}")
        else:
            print(entry)

    print()

    print("CONTENT DOCUMENTS")
    print("=================")

    for item in book.get_items_of_type(ITEM_DOCUMENT):
        inspect_document(item)


if __name__ == "__main__":
    main()
