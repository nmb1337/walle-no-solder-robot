# WALL-E v2 printable parts

`walle_parametric.scad` is the source of truth for the no-solder v2 design.
It targets a two-wheel, WALL-E-style robot built around bought 43 mm rubber
wheels, N20 motors, MG90S servos, and the Waveshare ESP32-S3-Touch-LCD-3.5-C
board with its supplied OV5640 camera.

The current V2 exports are in `stl_v2/`. Every part stays below the Bambu A1
`256 x 256 x 256 mm` build volume. The previous `stl/` directory and its
CoreS3 tray are superseded and must not be sent to print.

## First fit prints

1. `walle_n20_motor_clamp.stl` x2
2. `walle_battery_tray.stl` x1
3. `walle_touch_lcd_cradle.stl` x1
4. `walle_ov5640_camera_mount.stl` x1
5. `walle_mg90s_horn_adapter.stl` x6
6. `walle_ball_caster_plate.stl` x1
7. `walle_base_plate.stl` x1

Use PETG at 0.20 mm layer height, 4 walls, and 30% gyroid infill for structural
parts. Print the body, head and cosmetic track covers only after these parts
fit the bought hardware. Full dimensions and strict buying rules are in
`../DESIGN_FREEZE.md`; use `../docs/ASSEMBLY.md` and
`../docs/VALIDATION.md` for the assembly and release gates.
