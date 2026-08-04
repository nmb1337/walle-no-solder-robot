# Fit and no-solder audit

This document is the release gate between a plausible CAD layout and a robot
that can actually be assembled without soldering. A cart line is not a
permission to substitute a near match.

## Frozen interfaces

| Interface | Frozen requirement | CAD evidence |
| --- | --- | --- |
| Drive motor | N20, 6 V, 100 RPM, 3 mm D shaft, 150 mm pre-wired lead | Motor-clamp cavity `38.5 x 13.4 x 11.4 mm`; shaft centre Z = 25.5 mm. |
| Drive wheel | 43 mm outside diameter, <=19 mm wide, N20 D bore | Wheel centre Z = 25.5 mm and track-cover opening = 47 mm. |
| Battery | 2S protected pack, <=80 x 46 x 22 mm, XT30 | Tray inner envelope = 82 x 48 x 24 mm. |
| Articulation | MG90S, 180 degree, 22.8 x 12.2 x 28.5 mm | Servo cavities include 0.9-1.0 mm assembly allowance. |
| Display client | ESP32-S3-Touch-LCD-3.5-C case, 95.11 x 63.67 x 14.10 mm | Cradle opening = 97.11 x 65.67 mm. |
| Camera | supplied OV5640 carrier, <=28 x 28 mm | Mount cavity = 30 x 30 mm; connector direction remains a physical gate. |

The assembled decorative envelope is about `221 x 118 x 184 mm`; individual
printable parts remain within the Bambu A1 256 mm build volume.

## Current Taobao cart

| Cart line | Decision | Why |
| --- | --- | --- |
| ESP32-S3-Touch-LCD-3.5-C, case + camera | Buy | Exact Waveshare kit selected; it provides display, Wi-Fi, microphone, camera interface and speaker connector. Camera carrier still needs a dry fit. |
| 4 ohm / 3 W speaker with 1.25 mm plug | Buy | Exact 4 ohm / 3 W and the required pre-crimped 1.25 mm plug are selected. |
| 20 cm Dupont lead set | Buy | Pre-crimped male-to-male, male-to-female and female-to-female signal leads; no soldering. |
| ESP32-32D Type-C DevKitC-style board | Buy | Product photo shows fitted headers and the 53 x 27 mm board is retained by universal deck straps, not guessed hole positions. |
| PCA9685 purple board | Removed | Its listing did not provide sufficient evidence that the signal header is factory-soldered; replace only with a verified pre-soldered board. |
| MG90S 180 degree metal-gear servo x7 | Buy | Exact 180 degree option selected: six fitted plus one spare. First horn adapter is a dry-fit gate. |
| TB6612 dual motor driver board | Removed | Its listing did not provide sufficient evidence of a factory-soldered signal header and accessible STBY pin. |
| GA12-N20 drive motor x2 | Cart, verified | Selected variant is `6 V`, `100 RPM`, `3 mm D shaft` family, with `150 mm` pre-wired leads. CAD remains contingent on a first physical measurement. |
| D-axis rubber wheel x2 | Cart, verified | Selected variant is `43 mm` N20 wheel; CAD wheel diameter and shaft height have been updated to 43 mm / 25.5 mm. |

## Missing purchase gates

Do not buy or substitute these from a title alone:

1. One drive-motor spare: N20, 6 V, 100 RPM, 3 mm D shaft, no encoder
   extension, `10 x 12 x 34-36 mm`, pre-wired 2-pin lead, stall current <=0.8 A.
2. Wheel-width confirmation: the selected `43 mm` wheel must be `<=19 mm` wide
   and use a `3 mm D` bore rather than a round 3 mm bore.
3. Battery: protected 2S pack, `1500-2200 mAh`, XT30 output,
   `<=80 x 46 x 22 mm`, and a matched 8.4 V balance charger.
4. Power rails: fixed 5 V / 5-8 A and fixed 6 V / 3 A converters with screw
   terminals, each accepting 6.0-8.4 V input.
5. XT30 pigtail, 5 A inline fuse, terminal/lever distribution block, M2/M3
   screw kits, and a 15 mm ball caster with a shown mounting pattern.

## Questions to send sellers

Send the relevant line exactly before checking out a conditional candidate.

```text
N20: 请确认是6V、100RPM、3mm D型输出轴、无编码器加长尾部，
电机本体10x12mm、总长34-36mm、轴长至少9mm、堵转电流不超过0.8A；
请提供实物尺寸图，并确认已预装两芯线和插头。

轮子: 请确认外径42mm、轮宽不超过19mm、内孔是3mm D孔，
不是3mm圆孔或2mm孔；请提供尺寸图。

TB6612: 请确认双路板已焊好信号排针、带电机/电源螺丝端子，
STBY引脚可以接线，并提供正反面实物图。

电池: 请确认2S满电8.4V、带保护板、XT30放电口、尺寸不超过80x46x22mm，
并给出持续/峰值放电电流和匹配8.4V平衡充电器型号。

降压: 请确认输入范围覆盖6.0-8.4V，输出为固定5.0V且持续至少5A
（或固定6.0V且持续至少3A），并带已装好的螺丝端子。
```

## Electrical assembly verdict

The design can be assembled with no solder only when every current-carrying
joint is an XT30 plug, a pre-crimped connector, or a screw/lever terminal.
Signal leads are pre-crimped Dupont wires. The battery positive passes through
the 5 A fuse before splitting. Both regulated rails share ground; 6 V is only
for TB6612 `VM` and motors, while 5 V is for servos and logic. No item may be
wired directly to a bare PCB pad.

The final-shell print remains blocked until the motor, wheel, battery, camera
and horn dry fits have passed.
