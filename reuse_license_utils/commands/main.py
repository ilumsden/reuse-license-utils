# SPDX-FileCopyrightText: 2026 Ian Lumsden
#
# SPDX-License-Identifier: MIT

import argparse

from reuse_license_utils.commands.download_licenses import DownloadLicensesCommand
from reuse_license_utils.commands.generate_reuse import GenerateReuseTomlCommand
from reuse_license_utils.commands.headers import AddOrUpdateHeadersCommand
from reuse_license_utils.commands.print_expected import PrintExpectedCommand
from reuse_license_utils.commands.verify import VerifyCommand


def main() -> None:
    parser = argparse.ArgumentParser(description="Perform various utility operations on a repository using REUSE.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    cmd_objs = [
        GenerateReuseTomlCommand(),
        AddOrUpdateHeadersCommand(),
        DownloadLicensesCommand(),
        VerifyCommand(),
        PrintExpectedCommand(),
    ]
    for cmd in cmd_objs:
        cmd.setup(subparsers)
    args = parser.parse_args()
    args.func(args)
