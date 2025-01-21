from helpers import read_json, write_json
import logging


def add_prune_subcommand(parser):

    parser.add_argument("--platform", type=str, required=True, help="Platform to purge")

    parser.add_argument(
        "--no-prune-entities",
        action="store_false",
        dest="prune_entities",
        help="Do not prune entities from core.entity_registry",
    )
    parser.add_argument(
        "--no-prune-devices",
        action="store_false",
        dest="prune_devices",
        help="Do not prune devices from core.device_registry",
    )
    parser.add_argument(
        "--no-prune-state",
        action="store_false",
        dest="prune_state",
        help="Do not prune devices from core.device_registry",
    )

    parser.set_defaults(func=prune_subcommand)

    return parser


def prune_core_entity_registry(data, platform: str) -> tuple[dict, set, set]:
    deleted_entity_ids = set()
    deleted_device_ids = set()
    kept_entities = []

    for entity in data["data"]["entities"]:
        if entity["platform"] == platform:
            logging.debug(
                'Deleting entry from core.entity_registry["entities"], entity_id: %s, device_id: %s',
                entity["entity_id"],
                entity["device_id"],
            )
            deleted_entity_ids.add(entity["entity_id"])
            deleted_device_ids.add(entity["device_id"])
        else:
            kept_entities.append(entity)

    data["data"]["entities"] = kept_entities

    kept_entities = []
    for entity in data["data"]["deleted_entities"]:
        if entity["platform"] == platform:
            logging.debug(
                'Deleting entry from core.entity_registry["deleted_entities"], entity_id: %s, device_id: %s',
                entity["entity_id"],
                entity["device_id"],
            )
            deleted_entity_ids.add(entity["entity_id"])
            deleted_device_ids.add(entity["device_id"])
        else:
            kept_entities.append(entity)

    data["data"]["deleted_entities"] = kept_entities

    return data, deleted_entity_ids, deleted_device_ids


def prune_core_restore_state(states, deleted_entities: set):
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


def prune_core_device_registry(registry, deleted_devices: set):
    kept_devices = []
    for device in registry["data"]["devices"]:
        if device["id"] in deleted_devices:
            logging.debug(
                'Deleted device from core.device_registry["devices"], id: %s, name: %s',
                device["id"],
                device["name"],
            )
        else:
            kept_devices.append(device)
    registry["data"]["devices"] = kept_devices

    kept_devices = []
    for device in registry["data"]["deleted_devices"]:
        if device["id"] in deleted_devices:
            logging.debug(
                'Deleted device from core.device_registry["deleted_devices"], id: %s, name: %s',
                device["id"],
                device["name"],
            )
        else:
            kept_devices.append(device)

    registry["data"]["deleted_devices"] = kept_devices

    return registry


def prune_subcommand(args):
    core_entity_registry_file = args.path / ".storage" / "core.entity_registry"
    core_restore_state_file = args.path / ".storage" / "core.restore_state"
    core_device_registry_file = args.path / ".storage" / "core.device_registry"

    core_entity_registry = read_json(core_entity_registry_file)

    new_core_entity_registry, deleted_entities, deleted_devices = (
        prune_core_entity_registry(core_entity_registry, platform=args.platform)
    )

    core_restore_state = read_json(core_restore_state_file)

    new_core_restore_state = prune_core_restore_state(
        core_restore_state, deleted_entities
    )

    core_device_registry = read_json(core_device_registry_file)
    new_core_device_registry = prune_core_device_registry(
        core_device_registry, deleted_devices
    )

    logging.info("Writing files")
    write_json(
        core_entity_registry_file,
        new_core_entity_registry,
        args.dry_run or not args.prune_entities,
    )
    write_json(core_restore_state_file, new_core_restore_state, args.dry_run)
    write_json(
        core_device_registry_file,
        new_core_device_registry,
        args.dry_run or not args.prune_devices,
    )
