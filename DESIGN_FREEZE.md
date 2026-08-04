# WALL-E v2 design freeze

This is a no-solder, two-wheel WALL-E-style robot. It is intentionally not a
copy of the MakerWorld model. The MakerWorld page attributes its design to
other work under CC BY-NC-SA and its current print profile is not public, so
this project only uses it as visual and assembly reference.

## Mechanical envelope

All dimensions are millimetres. The source of truth is
`cad/walle_parametric.scad`.

| Printed / bought item | Frozen dimensions | Fit rule |
| --- | --- | --- |
| Base plate | 178 x 112 x 5 | Four M3 holes and battery straps |
| Body shell | 184 x 118 x 100 | Upper opening for service |
| Head shell | 182 x 90 x 76 | Front panel is removable |
| Face panel | 174 x 5 x 70 | Two 40 mm eye openings |
| Complete body, wheels included | about 240 wide x 118 deep x 184 high | Fits the A1 in separate parts |
| Drive wheels, bought | 42 diameter x 19 wide | 3 mm D-bore only, not round bore |
| N20 motor | 10 x 12 x 34-36 body, 3 mm D shaft, 6 V, 100 RPM | Must be pre-wired with a 2-pin connector |
| Motor clamp cavity | 38.5 x 13.4 x 11.4 | Cable tie slots; do not substitute a 25GA/370 motor |
| Battery tray internal envelope | 82 x 48 x 24 | Real pack must be no larger than 80 x 46 x 22 |
| MG90S servo envelope | 22.8 x 12.2 x 28.5 | Six 180-degree metal-gear units |
| ESP32-S3 audio board | 58 mm round board | 0.8 mm clearance in the printed cradle |
| OV2640 camera board | 35.7 x 23.9 | 24-pin 0.5 mm FPC version for the audio board |

The outer decorative side covers make the two-wheel chassis look like WALL-E
tracks. They are not load-bearing tracks. This is deliberate: two purchased
rubber wheels are quieter, easier to assemble, and reliable on tile and wood.

## Buy exactly these specifications

1. `Waveshare ESP32-S3-AUDIO-Board`, standard version, with dual microphone
   array, speaker header and 24-pin DVP camera connector. Do not buy an
   ESP32-S3-WROOM module alone: it needs soldering and has no ready audio path.
2. Compatible `OV2640 Camera Board`, `35.7 x 23.9 mm`, 24-pin, 0.5 mm FPC.
3. `ESP32 DevKitC V4`, USB-C and pre-soldered headers, for motors and servos.
4. Two `N20 6V 100 RPM` motors, `3 mm D shaft`, 10 x 12 x 34-36 mm. Buy the
   pre-wired 1.25 mm 2-pin version, plus one spare motor.
5. Two `42 x 19 mm` rubber robot wheels with a `3 mm D-bore`, not foam wheels
   and not a 2 mm or round bore wheel. This replaces TPU entirely.
6. `TB6612FNG` dual motor driver with pre-soldered signal header and screw
   terminals. It must have an accessible `STBY` pin.
7. `PCA9685` 16-channel servo board with pre-soldered headers.
8. Seven `MG90S 180-degree metal-gear` servos: six fitted, one spare. SG90,
   360-degree servos and 2 g aircraft servos are not compatible with this
   articulated design.
9. Protected `2S 7.4 V` Li-ion pack, maximum `80 x 46 x 22 mm`, with XT30
   output and an 8.4 V charger explicitly sold for that pack. Do not buy a
   18650 holder or a bare 18650 pack.
10. Fixed `5 V 10 A` buck converter with screw terminals for servos, ESP32
    DevKitC and the audio board. A 3 A converter is unsafe for six MG90S servos.
11. Fixed `6.0 V / 3 A` buck converter with screw terminals for TB6612 `VM`
    and the N20 motors. Do not connect a 2S battery directly to 6 V motors.
12. XT30 pre-made pigtail, 5 A inline fuse holder, 5 A fuse, 20 cm pre-crimped
    Dupont leads, and an M3 screw/standoff box. No stripping or soldering is
    required if every cable is bought pre-made.

The Taobao candidate [42 mm solid rubber N20 wheel](https://item.taobao.com/item.htm?id=657052441273)
does explicitly state `42 mm`, N20 compatibility and a `3 mm D-bore`. Its
page does not state wheel width, so ask the seller to confirm `19 mm or less`
before adding it to the cart. Do not substitute a different wheel just because
its title also says "N20".

## PETG and AMS Lite

Use PETG for every printed structural part. Do not put TPU in the AMS Lite.
If you have two PETG colours, load yellow in A and black in B. If you only
have one PETG spool, load it in A and print all parts in that material; colour
does not affect fitting. The bought rubber wheels provide grip.

Print and dry-fit before any large shell:

1. `cad/stl_v2/walle_n20_motor_clamp.stl`
2. One bought wheel and the motor shaft
3. `cad/stl_v2/walle_battery_tray.stl` with the real battery
4. `cad/stl_v2/walle_audio_core_cradle.stl` with the real ESP32-S3 board
5. `cad/stl_v2/walle_ov2640_camera_mount.stl` with the camera and FPC cable

The body and head are printed only after those five dry-fits pass. Also dry-fit
the MG90S horn adapter and rear ball-caster plate. The battery tray, motor
clamp, caster plate and horn adapter must be re-exported if a seller changes a
quoted physical dimension.

## Functional boundary

The gateway supports provider switching, text chat, image analysis, movement
and the standard OpenAI-compatible STT/TTS routes. The hardware is designed
for head yaw/pitch, two arms with shoulder/elbow joints, and two-wheel
movement. AI requests stay on the configured API, not on the 8100T.

Music playback must use a service and account that authorises playback. The
project will not promise access to an arbitrary percentage of copyrighted
catalogues or bypass a platform's controls.
