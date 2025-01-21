import logging, json
from pathlib import Path


def read_json(filename: Path):
    with open(filename, "r") as fstream:
        return json.load(fstream)


def write_json(filename: Path, data, dry_run=False):
    if dry_run:
        logging.info("Not writing to file %s", filename)
        return

    with open(filename, "wt") as fstream:
        logging.info("Writing file %s", filename)
        json.dump(data, fstream)
