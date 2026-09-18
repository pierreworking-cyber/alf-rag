from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import (
    Header,
    Label,
    ListItem,
    ListView,
    Static,
)

from tui.discuss_tui import DiscussTUI

class ALFRAGApp(App):
    """ALF-RAG TUI."""

    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    CSS = """
    Screen {
        layout: vertical;
        scrollbar-size: 1 1;
    }

    #main {
        height: 1fr;

    }

    #navigation {
        width: 25%;
        border: solid yellow;
    }

    #navigation ListItem.--highlight {
        text-style: bold;
    }

    #workspace {
        width: 75%;
        height: 1fr;
        layout: vertical;
    }

    #workspace-content {
        border: solid green;
        padding: 2;
    }

    #footer {
        height: 3;
        align: right middle;
    }

    #footer-guidance {
        width: 1fr;
        padding: 1 2;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()

        with Horizontal(id="main"):
            yield ListView(
                ListItem(
                    Label("Discuss a book"),
                    id="navigation-discuss",
                ),
                ListItem(
                    Label("Process new book"),
                    id="navigation-process",
                ),
                ListItem(
                    Label("Books"),
                    id="navigation-books",
                ),
                ListItem(
                    Label("Delete a book"),
                    id="navigation-delete",
                ),
                id="navigation",
            )

            with Vertical(id="workspace"):
                yield DiscussTUI(id="discuss-workspace")
                yield Static(
                    "Process a new book",
                    id="process-workspace",
                )
                yield Static(
                    "Books",
                    id="books-workspace",
                )
                yield Static(
                    "Delete a book",
                    id="delete-workspace",
                )

        with Horizontal(id="footer"):
            yield Static(
                "",
                id="footer-guidance",
            )

    def on_mount(self) -> None:
        navigation = self.query_one(
            "#navigation",
            ListView,
        )

        navigation.index = 0
        navigation.focus()

        self.show_workspace("discuss")


    def show_workspace(self, workspace: str) -> None:
        workspaces = {
            "discuss": self.query_one("#discuss-workspace"),
            "process": self.query_one("#process-workspace"),
            "books": self.query_one("#books-workspace"),
            "delete": self.query_one("#delete-workspace"),
        }

        guidance = {
            "discuss": "↑↓ Select   Enter Discuss   Q Quit",
            "process": "↑↓ Select   Enter Process   Q Quit",
            "books": "↑↓ Select   Enter Open   Q Quit",
            "delete": "↑↓ Select   Enter Delete   Q Quit",
        }

        for workspace_id, widget in workspaces.items():
            widget.display = workspace_id == workspace

        self.query_one(
            "#footer-guidance",
            Static,
        ).update(guidance[workspace])


    def on_list_view_highlighted(
        self,
        event: ListView.Highlighted,
    ) -> None:
        if event.list_view.id != "navigation":
            return

        if event.item is None:
            return

        workspace = event.item.id.removeprefix(
            "navigation-"
        )

        self.show_workspace(workspace)


if __name__ == "__main__":
    ALFRAGApp().run()
