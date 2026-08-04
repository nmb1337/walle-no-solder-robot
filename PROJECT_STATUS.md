# Project status

## Completed

- Windows gateway with API profile storage that excludes secrets from source.
- Text and image relay support, dashboard movement controls and a one-second
  motion watchdog in the ESP32 controller.
- Original V2 OpenSCAD source and A1-bounded STL exports.
- No-solder BOM, PETG print guide, assembly guide and engineering validation.
- Static checks: gateway Python syntax, action translation, and V2 STL bounds.

## Required before full build

- Seller confirms motor shaft, wheel width/bore, battery dimensions and motor
  stall current against `docs/BOM.md`.
- Fit prints pass with real motor, wheel, battery, audio board, camera,
  supplied servo horn and ball caster.
- Regulated rails measure exactly 5.0 V and 6.0 V before electronics connect.
- Bench-test motors, six servos, watchdog, camera upload and API image call.

No purchase, order, payment, or printer job is submitted by this repository.
