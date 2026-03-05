# SPDX-FileCopyrightText: 2026 Ian Lumsden
#
# SPDX-License-Identifier: MIT

import argparse

from reuse_license_utils.commands.command_base import Command
from reuse_license_utils.headers import add_headers


class AddOrUpdateHeadersCommand(Command):
    def __init__(self) -> None:
        super().__init__("add-headers", "Add or update SPDX headers in source code files specified by the config")

    def _add_subcommand_specific_arguments(self) -> None:
        self.parser.add_argument(
            "--use-uv",
            "-u",
            action="store_true",
            help="If provided, invoke REUSE using `uv` instead of invoking directly",
        )
        self.parser.add_argument(
            "--overwrite-copyright-lines",
            "-o",
            action="store_true",
            help="If provided, remove all SPDX-FileCopyrightText lines for a given copyright holder before generating new headers",  # noqa: E501
        )

    def _run_impl(self, args: argparse.Namespace) -> None:
        add_headers(
            repo_root=self.repo_root,
            config=self.config,
            use_uv=args.use_uv,
            overwrite_copyright_lines=args.overwrite_copyright_lines,
        )
        print("License headers have been added/updated for all your source code files!")
