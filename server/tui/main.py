from textual.app import App, ComposeResult
from textual.widgets import Header, Footer

from textual.containers import Container
from textual.containers import Vertical
from textual.widgets import Button, Static , MarkdownViewer,DirectoryTree,Label
from textual.reactive import var
from textual.scroll_view import ScrollView

from pathlib import Path


from rich.syntax import Syntax
from rich.traceback import Traceback

class UIFrame(Static):
    """A stopwatch widget."""

    def compose(self) -> ComposeResult:
        """Create child widgets of a stopwatch."""
        yield Button("Start", id="start", variant="success")
        yield Button("Stop", id="stop", variant="error")
        yield Button("Reset", id="reset")

class LightAPTTui(App):
    """
        LightAPT Terminal UI for debugging and remote controlling
    """

    path = var(Path(__file__).parent.parent.parent / "README.md")
    show_tree = var(True)

    CSS_PATH = "main.css"
    BINDINGS = [("d", "toggle_dark", "暗色模式"),
                ("q", "quit", "退出"),
                ("t", "toggle_table_of_contents", "目录树"),
                ("b", "back", "后退"),
                ("f", "forward", "向前"),
                ("s", "toggle_files", "Toggle Files"),
                ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        self.title = "LightAPT TUI"
        yield Header()
        yield ScrollView(MarkdownViewer())
        yield Label("文件目录",expand=True,id="label-title")
        yield ScrollView(
            DirectoryTree(str(Path(__file__).parent.parent.parent), id="tree-view"),
            Vertical(Static(id="code", expand=True), id="code-view"),
            )
        yield Footer()
        
        
    def watch_show_tree(self, show_tree: bool) -> None:
        """Called when show_tree is modified."""
        self.set_class(show_tree, "-show-tree")


    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark
        
    @property
    def markdown_viewer(self) -> MarkdownViewer:
        """Get the Markdown widget."""
        return self.query_one(MarkdownViewer)
    
    async def on_mount(self) -> None:
        self.markdown_viewer.focus()
        self.query_one(DirectoryTree).focus()
        if not await self.markdown_viewer.go(self.path):
            self.exit(message=f"Unable to load {self.path!r}")

    def action_toggle_table_of_contents(self) -> None:
        self.markdown_viewer.show_table_of_contents = (
            not self.markdown_viewer.show_table_of_contents
        )

    async def action_back(self) -> None:
        await self.markdown_viewer.back()

    async def action_forward(self) -> None:
        await self.markdown_viewer.forward()

    def on_directory_tree_file_selected(
        self, event: DirectoryTree.FileSelected
    ) -> None:
        """Called when the user click a file in the directory tree."""
        event.stop()
        code_view = self.query_one("#code", Static)
        try:
            syntax = Syntax.from_path(
                event.path,
                line_numbers=True,
                word_wrap=False,
                indent_guides=True,
                theme="github-dark",
            )
        except Exception:
            code_view.update(Traceback(theme="github-dark", width=None))
            self.sub_title = "ERROR"
        else:
            code_view.update(syntax)
            self.query_one("#code-view").scroll_home(animate=False)
            self.sub_title = event.path

    def action_toggle_files(self) -> None:
        """Called in response to key binding."""
        self.show_tree = not self.show_tree

if __name__ == "__main__":
    app = LightAPTTui()
    app.run()