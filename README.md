# WALL-E no-solder robot gateway

An A1-sized, PETG-printed WALL-E-style robot with two differential-drive
wheels, six positional joints, ESP32-S3 camera/audio hardware, and a Windows
LAN gateway for API-based text and image intelligence.

This is an original parameterised chassis. It is visually inspired by WALL-E
and studies of public community projects, but it does not redistribute or copy
another creator's STL files.

## Read these first

1. [Design dimensions and strict fit rules](DESIGN_FREEZE.md)
2. [No-solder bill of materials](docs/BOM.md)
3. [Assembly guide](docs/ASSEMBLY.md)
4. [Engineering validation and release gates](docs/VALIDATION.md)
5. [PETG / AMS Lite setup](shopping/ams-lite-setup.md)

The project is intentionally blocked from full-shell printing until the five
fit parts pass with the bought hardware. This prevents a wrong wheel bore,
battery pack, motor shaft or camera connector from turning into a large failed
print.

## Software

Run the local gateway with `start-gateway.ps1`. It serves the dashboard on
`http://127.0.0.1:8100` and exposes API-compatible text, image, motion, camera
and optional STT/TTS routes. API keys stay only in `gateway-config.json`, which
is not included in the project package.

The motor ESP32 polls the gateway for movement and joint events. It has a
one-second motor watchdog and starts stopped. See `firmware/README.md` before
connecting any battery.

## Print source

The source is `cad/walle_parametric.scad`; rendered V2 parts are in
`cad/stl_v2/`. Every V2 STL has been checked against the Bambu Lab A1
`256 x 256 x 256 mm` build volume. Print PETG fit parts first, then proceed in
the order in `docs/ASSEMBLY.md`.
