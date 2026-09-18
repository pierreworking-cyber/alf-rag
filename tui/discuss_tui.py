from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Label, ListItem, ListView

import documents


class DiscussTUI(Vertical):
    def compose(self) -> ComposeResult:
        yield Label("Select a book to discuss:")

        books = [
            path
            for path in documents.available_documents()
            if documents.is_processed(path)
        ]

        yield ListView(
            *[
                ListItem(
                    Label(path.stem),
                    id=f"book-{index}",
                )
                for index, path in enumerate(books)
            ],
            id="discuss-books",
        )
