# SPDX-FileCopyrightText: 2026 Ian Lumsden
#
# SPDX-License-Identifier: MIT

import argparse
from pathlib import Path

from reuse_license_utils.commands.command_base import Command
from reuse_license_utils.files import collect_header_files, collect_reuse_toml_files


class PrintExpectedCommand(Command):
    def __init__(self) -> None:
        super().__init__(
            "print-expected",
            "Print the files that should either have license headers or should be in REUSE.toml",
        )

    def _add_subcommand_specific_arguments(self) -> None:
        self.parser.add_argument(
            "headers_or_toml",
            type=str,
            choices=("headers", "toml"),
            help=(
                "If 'headers', print the files that should contain license headers. "
                "If 'toml', print the files that should be represented in REUSE.toml"
            ),
        )

    def _print_information(self, files: list[Path], info_header: str) -> None:
        content_for_group = info_header
        if info_header[-1] != "\n":
            content_for_group += "\n"
        content_for_group += "\n".join([f"  - {f!s}" for f in files])
        print(content_for_group, end="\n\n")

    def _run_impl(self, args: argparse.Namespace) -> None:
        if args.headers_or_toml == "headers":
            header = "Files that should include headers:"
            print(header)
            print("=" * len(header), end="\n\n")
            for group_id in self.config.header_groups.keys():
                header_files = collect_header_files(self.repo_root, self.config, group_id)
                self._print_information(header_files, f"Files for header group {group_id}:")
        else:
            header = "Files that should be in REUSE.toml:\n"
            header += "=" * (len(header) - 1)
            toml_files = collect_reuse_toml_files(self.repo_root, self.config)
            self._print_information(toml_files, header)
