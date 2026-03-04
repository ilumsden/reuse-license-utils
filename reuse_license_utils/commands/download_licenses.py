import argparse
import sys

from reuse_license_utils.commands.command_base import Command
from reuse_license_utils.licenses import download_licenses


class DownloadLicensesCommand(Command):
    def __init__(self) -> None:
        super().__init__("download-licenses", "Download license files for all licenses in the config")

    def _add_subcommand_specific_arguments(self) -> None:
        self.parser.add_argument(
            "--use-uv",
            "-u",
            action="store_true",
            help="If provided, invoke REUSE using `uv` instead of invoking directly",
        )

    def _run_impl(self, args: argparse.Namespace) -> None:
        # Build a full set of license IDs from the config
        license_ids = set()
        # Add the default license ID to the set if it is not None
        if self.config.default_license_id is not None:
            license_ids.add(self.config.default_license_id)
        # Add any license IDs from the `header_groups` section of the config to the set
        for header_config in self.config.header_groups.values():
            if header_config.license_id is not None:
                license_ids.add(header_config.license_id)
        # Add any license IDs from the `reuse_toml_paths` section of the config to the set
        for reuse_toml_path_config in self.config.reuse_toml_paths:
            if reuse_toml_path_config.license_id is not None:
                license_ids.add(reuse_toml_path_config.license_id)

        # Download licenses
        successful_licenses, failed_licenses = download_licenses(
            repo_root=self.repo_root,
            license_ids=list(license_ids),
            use_uv=args.use_uv,
        )

        # Print information about licenses that were successfully downloaded
        print("The following licenses were successfully downloaded:")
        for successful_license_name in successful_licenses:
            print(f"  - {successful_license_name}")
        print()

        # Print information about licenses that failed to download
        if len(failed_licenses) > 0:
            print("The following licenses failed to download:", file=sys.stderr)
            for failed_license_name in failed_licenses:
                print(f"  - {failed_license_name}", file=sys.stderr)

        print(f"You can find all downloaded files in {self.repo_root / 'LICENSES'}.")
