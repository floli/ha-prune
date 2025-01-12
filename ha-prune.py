#!/usr/bin/env python3

import argparse, logging, json, sys
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dry-run",
        "-n",
        action="store_true",
        help="Do not write anything to disk",
    )
    parser.add_argument("--platform", type=str, required=True, help="Platform to purge")
    parser.add_argument(
        "--path",
        type=Path,
        help="Home Assistant's config directory (the one where the .storage directory is in)",
    )
    args = parser.parse_args()

    if not args.path.is_dir():
        print("Base path not found or no directory.")
        sys.exit(-1)

    return args


def read_json(filename: Path):
    with open(filename, "r") as fstream:
        return json.load(fstream)


def write_json(filename: Path, data, dry_run=False):
    if dry_run:
        logging.info("Dry run, not writing to file %s", filename)
        return

    with open(filename, "wt") as fstream:
        logging.info("Writing file %s", filename)
        json.dump(data, fstream)


def prune_core_entity_registry(data, platform: str) -> list:
    deleted_entity_ids = []
    kept_entities = []

    for entity in data["data"]["entities"]:
        if entity["platform"] == platform:
            logging.debug(
                'Deleting entry from core.entity_registry["entities"], id: %s',
                entity["entity_id"],
            )
            deleted_entity_ids.append(entity["entity_id"])
        else:
            kept_entities.append(entity)

    data["data"]["entities"] = kept_entities
    kept_entities = []

    for entity in data["data"]["deleted_entities"]:
        if entity["platform"] == platform:
            logging.debug(
                'Deleting entry from core.entity_registry["deleted_entities"], id: %s',
                entity["entity_id"],
            )
            deleted_entity_ids.append(entity["entity_id"])
        else:
            kept_entities.append(entity)

    data["data"]["deleted_entities"] = kept_entities

    logging.info(
        "Deleted %s entries from core.entity_registry", len(deleted_entity_ids)
    )
    return data, deleted_entity_ids


def prune_core_restore_state(states, deleted_entities):
    kept_states = []
    for state in states["data"]:
        if state["state"]["entity_id"] in deleted_entities:
            logging.debug(
                "Deleting entry from core.restore_state, id: %s",
                state["state"]["entity_id"],
            )
        else:
            kept_states.append(state)
    states["data"] = kept_states
    return states


def main():
    logging.basicConfig(level=logging.DEBUG)
    args = parse_args()

    core_entity_registry_file = args.path / ".storage" / "core.entity_registry"
    core_restore_state_file = args.path / ".storage" / "core.restore_state"

    core_entity_registry = read_json(core_entity_registry_file)

    new_core_entity_registry, deleted_entities = prune_core_entity_registry(
        core_entity_registry, platform=args.platform
    )

    core_restore_state = read_json(core_restore_state_file)

    new_core_restore_state = prune_core_restore_state(
        core_restore_state, deleted_entities
    )

    logging.info("Writing files")
    write_json(core_entity_registry_file, new_core_entity_registry, args.dry_run)
    write_json(core_restore_state_file, new_core_restore_state, args.dry_run)


if __name__ == "__main__":
    main()
