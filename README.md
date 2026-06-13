# AirMaster 7 Plus — Home Assistant Integration

[![GitHub Release](https://img.shields.io/github/v/release/SkeLLLa/hass-airmaster7plus?style=flat-square)](https://github.com/SkeLLLa/hass-airmaster7plus/releases)
[![License](https://img.shields.io/github/license/SkeLLLa/hass-airmaster7plus?style=flat-square)](LICENSE)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=flat-square)](https://github.com/hacs/integration)
[![CI](https://img.shields.io/github/actions/workflow/status/SkeLLLa/hass-airmaster7plus/validate.yml?branch=master&style=flat-square&label=CI)](https://github.com/SkeLLLa/hass-airmaster7plus/actions/workflows/validate.yml)

Native Home Assistant integration for the **AirMaster 7 Plus (AM7P)** air quality monitor.

Listens for the device's UDP broadcasts on the local network and exposes its readings
as Home Assistant entities. **No MQTT broker required** — data flows straight into HA.

Based on earlier AirMaster community work.

## Features

- Local push: device pushes UDP packets, integration parses them in-process.
- Auto-discovery: each AM7P (by source IP) becomes a HA device with its own sensors.
- UI config flow — no YAML.

## Sensors

| Entity      | Device class                 | Unit  |
| ----------- | ---------------------------- | ----- |
| PM2.5       | pm25                         | µg/m³ |
| PM10        | pm10                         | µg/m³ |
| HCHO        | volatile_organic_compounds   | mg/m³ |
| TVOC        | volatile_organic_compounds   | mg/m³ |
| CO₂         | carbon_dioxide               | ppm   |
| Temperature | temperature                  | °C    |
| Humidity    | humidity                     | %     |
| Online      | connectivity (binary_sensor) | —     |

The integration also exposes a disabled-by-default diagnostic sensor for the
timestamp of the last update received from the device.

## Installation (HACS)

### Add this repo manually to HACS

1. Open HACS in Home Assistant.
2. Go to `Integrations`.
3. Open the top-right menu (`⋮`) and select `Custom repositories`.
4. In `Repository`, paste this repo URL:

```text
https://github.com/SkeLLLa/hass-airmaster7plus
```

5. In `Category`, select `Integration`.
6. Click `Add`.

### Install the integration

1. Find `AirMaster 7 Plus` in HACS Integrations.
2. Click `Download`.
3. Restart Home Assistant.
4. Go to `Settings` → `Devices & Services`.
5. Click `Add Integration` and select `AirMaster 7 Plus`.
6. Set the UDP port (default `12414`). Devices appear on first received packet.

## Requirements

- AM7P configured to send UDP to your HA host's network (see AirMasterConnect for Wi-Fi setup).
- Static IP / DHCP reservation for the device recommended — a changed IP is treated as a new device.

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
