# Home Assistant Prune

**DISCLAIMER: Use at your own risk!** It has worked for me, it might not work for you, or even worse screw your system or eat your favorite pet.

Pull Requests, Bug Reports and Thank You are welcome and appreciated.

## Problem Statement

Devices can be renamed outside of Home Assistant. When this happens, the integration does not propagate that change to Home Assistant, i.e., the `entity_id` is not changed. This makes sense to not break automations etc.

On the other hand, that causes names outside and inside of Home Assistant to diverge over time. See this [feature request](https://community.home-assistant.io/t/reset-re-acquire-entity-id/723097) for concrete user stories.

Unfortunately, Home Assistant lacks a functionality to re-acquire the current names from the integrations.

Some forum ports that are related to the problem:

- Feature Request (please vote!): [Reset / Re-acquire entity_id](https://community.home-assistant.io/t/reset-re-acquire-entity-id/723097)
- Question: [Reset Hue entity ids?](https://community.home-assistant.io/t/reset-hue-entity-ids/583524)
- Question: [Reset entity_id after name change](https://community.home-assistant.io/t/reset-entity-id-after-name-change/485269)
- Question: [Rename entity_id for script any solutions?](https://community.home-assistant.io/t/rename-entity-id-for-script-any-solutions/338037)
- Question: [Rename an Entity ID](https://community.home-assistant.io/t/rename-an-entity-id/608186)

## Solution Approach
1. Remove all entities from file `core.entity_registry` where `platform` matches.
2. Remove the same entities from file `core.restore_state`, if existing.
3. Remove the devices with matching `id` from file `core.device_registry`.


## Usage
First of all, stop Home Assistant. To my experience, the integration/platform does not need to be removed.

Backup your configuration directory. The script does not do backups.

### Prune Entities

Run, e.g.

```
ha-prune.py --path homeassistant-config prune --platform hue
```

Use `--dry-run` or `-n` to not actually write anything to disk.

Restart Home Assistant. The entities should be automatically re-discovered under their new name (i.e. the names obtained from the integration).

### Save and restore (friendly) names

The command:

```
ha-prune.py --path homeassistant-config save "out.json"
```

saves the friendly names, if set, for all entities. It produces a file like:

```
{
    "switch.horus": "Horus",
    "sensor.sentinel_1_air_temperature": "Flur",
    "device_tracker.thermostat_wohnzimmer": "Thermostat Wohnzimmer",
    "switch.janus_1": "Heizlüfter",
}
```

vice versa

```
ha-prune.py --path homeassistant-config restore out.json
```

restores the friendly names, if modified.

## Known Problems

### Unstable IDs
IDs like

```json
device_id: c42cc5888a0c7349d8425023efdedac7
entity_id: 28b1c57400b2c8bc5930b8889505edcb
```

seem to be unstable when devices are re-discovered. Use `entity_id` like `light.kitchen` in your automations etc.