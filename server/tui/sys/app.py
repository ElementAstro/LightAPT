from __future__ import annotations

import argparse
from sys import version_info

from textual.app import App

from .version import __version__
from .cpu import CPU
from .disk import Disk
from .info import InfoLine
from .mem import Mem
from .network import Net
from .procs_list import ProcsList

def run(argv=None):
    parser = argparse.ArgumentParser(
        description="Command-line system monitor.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version=_get_version_text(),
        help="display version information",
    )

    parser.add_argument(
        "--log",
        "-l",
        type=str,
        default=None,
        help="debug log file",
    )

    parser.add_argument(
        "--net",
        "-n",
        type=str,
        default=None,
        help="network interface to display (default: auto)",
    )

    args = parser.parse_args(argv)

    # with a grid
    class TiptopApp(App):
        async def on_mount(self) -> None:
            grid = await self.view.dock_grid(edge="left")

            grid.add_column(fraction=55, name="left")
            grid.add_column(fraction=34, name="right")

            grid.add_row(size=1, name="r0")
            grid.add_row(fraction=1, name="r1")
            grid.add_row(fraction=1, name="r2")
            grid.add_row(fraction=1, name="r3")
            grid.add_areas(
                area0="left-start|right-end,r0",
                area1="left,r1",
                area2a="right,r1",
                area2b="right,r2",
                area2c="right,r3",
                area3="left,r2-start|r3-end",
            )
            grid.place(
                area0=InfoLine(),
                area1=CPU(),
                area2a=Mem(),
                area2b=Disk(),
                area2c=Net(args.net),
                area3=ProcsList(),
            )

        async def on_load(self, _):
            await self.bind("q", "quit", "quit")

    TiptopApp.run(log=args.log)


def _get_version_text():
    python_version = f"{version_info.major}.{version_info.minor}.{version_info.micro}"

    return "\n".join(
        [
            f"tiptop {__version__} [Python {python_version}] Modified for LightAPT Lanucher",
            "Copyright (c) 2021-2022 Nico Schlömer",
            "Copyright (c) 2022-2023 Max Qian",
        ]
    )
