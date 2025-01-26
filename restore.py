import argparse, pathlib
from helpers import read_json, write_json
import logging


def add_restore_subcommand(parser: argparse.ArgumentParser):
    parser.add_argument(
        "infile",
        type=pathlib.Path,
        help="Input filename containing the names to restore",
    )

    parser.set_defaults(func=restore_subcommand)
    return parser


def restore_subcommand(args):
    core_entity_registry_file = args.path / ".storage" / "core.entity_registry"
    data = read_json(core_entity_registry_file)
    in_data = read_json(args.infile)
    dirty = False

    for entity in data["data"]["entities"]:
        id = entity["entity_id"]
        if id in in_data and entity["name"] != in_data[id]:
            entity["name"] = in_data[id]
            dirty = True
            logging.debug("Restored name %s for id %s", in_data[id], id)

    if dirty:
        write_json(core_entity_registry_file, data, args.dry_run)
