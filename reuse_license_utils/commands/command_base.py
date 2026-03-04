# SPDX-FileCopyrightText: 2026 Ian Lumsden
#
# SPDX-License-Identifier: MIT

import argparse
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from reuse_license_utils.config import load_config
from reuse_license_utils.utils import find_pyproject_toml, find_repo_root


class Command(ABC):
    def __init__(self, subcommand_name: str, description: str | None = None) -> None:
        self.subcommand_name = subcommand_name
        self.description = description
        self.parser = None
        self.repo_root = None
        self.config = None

    def setup(self, subparsers: Any) -> None:
        self.parser = self.create_subparser(subparsers)
        self._add_subcommand_specific_arguments()
        self.parser.set_defaults(func=self.run)

    def create_subparser(self, subparsers: Any) -> argparse.ArgumentParser:
        parser = subparsers.add_parser(
            self.subcommand_name,
            help=self.description if self.description is not None else "",
        )
        parser.add_argument(
            "--repo-root",
            "-r",
            type=Path,
            default=None,
            help=(
                "The path to the root of the repository for which to use REUSE."
                "If not provided, GitPython is used to autodetect the path based on the current working directory."
            ),
        )
        parser.add_argument(
            "--config-file",
            "-c",
            type=Path,
            default=None,
            help=(
                "The path to the config file for reuse-license-utils."
                "If not provided, the `pyproject.toml` file under `repo-root` will be used."
            ),
        )
        return parser

    def run(self, args: argparse.Namespace) -> None:
        if args.config_file is not None and args.repo_root is None:
            raise ValueError("When `--config-file` is provided, `--repo-root` must also be provided.")
        self.repo_root = args.repo_root
        if args.repo_root is None:
            self.repo_root = find_repo_root()
        self.repo_root = self.repo_root.expanduser().resolve()
        config_file = args.config_file
        if args.config_file is None:
            config_file = find_pyproject_toml(self.repo_root)
            if config_file is None:
                raise FileNotFoundError("Cannot find a config file or `pyproject.toml` file for reuse-license-utils")
        config_file = config_file.expanduser().resolve()
        self.config = load_config(config_file)
        self._run_impl(args)

    @abstractmethod
    def _add_subcommand_specific_arguments(self) -> None:
        pass

    @abstractmethod
    def _run_impl(self, args: argparse.Namespace) -> None:
        pass
