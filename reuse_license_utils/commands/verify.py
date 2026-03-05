# SPDX-FileCopyrightText: 2026 Ian Lumsden
#
# SPDX-License-Identifier: MIT

import argparse
import sys

from reuse_license_utils.commands.command_base import Command
from reuse_license_utils.verify import verify_repo


class VerifyCommand(Command):
    def __init__(self) -> None:
        super().__init__("verify", "Verify that the repository adheres to the REUSE spec")

    def _add_subcommand_specific_arguments(self) -> None:
        self.parser.add_argument(
            "--use-uv",
            "-u",
            action="store_true",
            help="If provided, invoke REUSE using `uv` instead of invoking directly",
        )
        self.parser.add_argument(
            "--quiet",
            "-q",
            action="store_true",
            help="If provided, pass `--quiet` to `reuse lint`",
        )

    def _run_impl(self, args: argparse.Namespace) -> None:
        subprocess_cmd = verify_repo(
            repo_root=self.repo_root,
            use_uv=args.use_uv,
            quiet=args.quiet,
            check=False,
        )
        if subprocess_cmd.returncode != 0:
            print("The repository is NOT REUSE-compliant!", file=sys.stderr)
            sys.exit(subprocess_cmd.returncode)
        print("The repository is REUSE-compliant!")
