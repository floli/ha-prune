# Known Problems

## Unstable IDs
IDs like

```json
device_id: c42cc5888a0c7349d8425023efdedac7
entity_id: 28b1c57400b2c8bc5930b8889505edcb
```

seem to be unstable when devices are re-discovered. Use `entity_id` like `light.kitchen` in your automations etc.