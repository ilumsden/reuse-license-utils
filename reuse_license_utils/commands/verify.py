import argparse

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
        verify_repo(
            repo_root=self.repo_root,
            use_uv=args.use_uv,
            quiet=args.quiet,
            check=True,
        )
