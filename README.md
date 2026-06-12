# AirMaster 7 Plus — Home Assistant Integration

Native Home Assistant integration for the **AirMaster 7 Plus (AM7P)** air quality monitor.

Listens for the device's UDP broadcasts on the local network and exposes its readings
as Home Assistant entities. **No MQTT broker required** — data flows straight into HA.

Based on earlier AirMaster community work.

## Features

- Local push: device pushes UDP packets, integration parses them in-process.
- Auto-discovery: each AM7P (by source IP) becomes a HA device with its own sensors.
- UI config flow — no YAML.

## Sensors

| Entity | Device class | Unit |
|---|---|---|
| PM2.5 | pm25 | µg/m³ |
| PM10 | pm10 | µg/m³ |
| HCHO | volatile_organic_compounds | mg/m³ |
| TVOC | volatile_organic_compounds | mg/m³ |
| CO₂ | carbon_dioxide | ppm |
| Temperature | temperature | °C |
| Humidity | humidity | % |
| Online | connectivity (binary_sensor) | — |

The integration also exposes a disabled-by-default diagnostic sensor for the
timestamp of the last update received from the device.

## Installation (HACS)

1. HACS → Integrations → ⋮ → Custom repositories.
2. Add this repo URL, category **Integration**.
3. Install **AirMaster 7 Plus**, restart Home Assistant.
4. Settings → Devices & Services → Add Integration → **AirMaster 7 Plus**.
5. Set the UDP port (default `12414`). Devices appear on first received packet.

## Requirements

- AM7P configured to send UDP to your HA host's network (see AirMasterConnect for Wi-Fi setup).
- Static IP / DHCP reservation for the device recommended — a changed IP is treated as a new device.

## Development

See `.tmp/INTEGRATION_PLAN.md` for the build plan and the reference Python scripts
(`am7p_bridge.py`, `am7p_monitor.py`, `am7p_publish.py`) the integration is derived from.

## Credits

- [reejk/AirMasterConnect](https://github.com/reejk/AirMasterConnect/) for the original implementation and the app used to onboard the AirMaster device onto Wi-Fi.
- [director-coder/AirMasterBridge](https://github.com/director-coder/AirMasterBridge) for the AirMaster add-on/app that provided the UDP-to-MQTT bridge approach this integration builds on.

Run tests:

```bash
pip install -r requirements_test.txt
pytest -q
```

## Releases

Releases are automated, semantic-release style. On every push to `master`,
`.github/workflows/release.yml` runs [python-semantic-release]: it reads
[Conventional Commits], computes the next version, bumps `version` in
`manifest.json`, creates the git tag (`vX.Y.Z`), and publishes a GitHub release
with an auto-generated changelog. HACS installs from that tag.

Commit message → version bump:

- `fix: ...` → patch
- `feat: ...` → minor
- `feat!: ...` / `BREAKING CHANGE:` → major

`.github/workflows/validate.yml` runs hassfest, HACS validation, and tests on
every push and PR.

[python-semantic-release]: https://python-semantic-release.readthedocs.io/
[Conventional Commits]: https://www.conventionalcommits.org/
