#!/usr/bin/env python3

import argparse, logging, json, sys
from pathlib import Path


import prune


def rename_subcommand(parser):
    return parser


def save_subcommand(parser):
    return parser


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--path",
        type=Path,
        help="Home Assistant's config directory (the one where the .storage directory is in)",
    )
    parser.add_argument(
        "--dry-run",
        "-n",
        action="store_true",
        help="Do not write anything to disk",
    )

    subparsers = parser.add_subparsers(help="subcommand help")
    subparser = subparsers.add_parser("prune", help="prune help")
    prune.add_prune_subcommand(subparser)

    subparser = subparsers.add_parser("rename", help="Rename an entity")
    rename_subcommand(subparser)

    subparser = subparsers.add_parser("save", help="Save attributes of entities")
    save_subcommand(subparser)

    args = parser.parse_args()

    if not args.path.is_dir():
        print("Base path not found or no directory.")
        sys.exit(-1)

    return args


def main():
    logging.basicConfig(level=logging.DEBUG)
    args = parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
