# Contributing

## Reporting Issues

Open an issue at https://github.com/SkeLLLa/hass-airmaster7plus/issues.
Include your HA version, integration version, and relevant logs.

## Development Setup

```bash
git clone https://github.com/SkeLLLa/hass-airmaster7plus.git
cd hass-airmaster7plus
pip install -r requirements_test.txt
```

## Running Tests

```bash
pytest -q
```

## Pull Requests

- Follow [Conventional Commits](https://www.conventionalcommits.org/) — releases are automated from commit messages.
- `fix:` → patch, `feat:` → minor, `feat!:` / `BREAKING CHANGE:` → major.
- One logical change per PR.
- Tests must pass (`pytest -q`).
- CI runs hassfest, HACS validation, and tests automatically on every PR.

## Commit Message Format

```
type(scope): short description

# Examples
fix: correct TVOC unit conversion
feat: add CO2 trend sensor
feat!: rename domain from am7p to airmaster7plus
```
