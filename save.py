import argparse, pathlib
from helpers import read_json, write_json


def add_save_subcommand(parser: argparse.ArgumentParser):

    parser.add_argument("outfile", type=pathlib.Path, help="Output file path")

    parser.set_defaults(func=save_subcommand)

    return parser


def save_subcommand(args):
    core_entity_registry_file = args.path / ".storage" / "core.entity_registry"
    data = read_json(core_entity_registry_file)

    names = {}

    for entity in data["data"]["entities"]:
        if entity["name"] is not None:
            names[entity["entity_id"]] = entity["name"]

    write_json(args.outfile, names, args.dry_run)
