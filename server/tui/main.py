from textual.app import App, ComposeResult
from textual.widgets import Header, Footer

from textual.containers import Container
from textual.widgets import Button, Static

class Stopwatch(Static):
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

    CSS_PATH = "main.css"
    BINDINGS = [("d", "toggle_dark", "暗色模式"),
                ("q", "quit", "退出")
                ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        self.title = "LightAPT TUI"
        yield Header()
        yield Footer()
        yield Container(Stopwatch())

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark


if __name__ == "__main__":
    app = LightAPTTui()
    app.run()