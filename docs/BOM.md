# No-solder BOM

Buy by the **specification column**, not only by the title. A listing with a
different shaft, plug, voltage, or physical size is not a compatible
substitute. Prices change often, so this list intentionally avoids promising
one seller or one price.

## Motion and structure

| Qty | Exact specification | Maximum envelope / interface | Search words |
| --- | --- | --- | --- |
| 3 | N20 metal gearmotor, 6 V, 100 RPM, 3 mm D shaft, 10 x 12 x 34-36 mm | Stall current <= 0.8 A; pre-wired MX1.25 2P lead; two fitted + one spare | `N20 6V 100转 3mm D轴 带线 1.25` |
| 2 | Solid rubber wheel, 42 mm OD, <= 19 mm width, 3 mm D-bore | No foam, no round bore, no 2 mm shaft version | `42mm 橡胶实心轮 N20 3mm D孔` |
| 7 | MG90S metal-gear, 180 degree servo | 22.8 x 12.2 x 28.5 mm; six fitted + one spare | `MG90S 金属齿 180度` |
| 1 | 15 mm ball caster, complete assembly | body <= 20 x 20 x 16 mm; M2 mounting pattern must be shown | `15mm 万向滚球 小车` |
| 1 | M2 screw/nut kit | M2 x 6 and M2 x 8 for supplied servo horns | `M2 螺丝螺母盒` |
| 1 | M3 screw/standoff kit | M3 x 8/10/12/14/16 and M3 nuts | `M3 铜柱螺丝盒` |

## Electronics

| Qty | Exact specification | Required detail-page evidence | Search words |
| --- | --- | --- | --- |
| 1 | Waveshare ESP32-S3-AUDIO-Board, standard board | 58 mm round board; dual microphones, 24-pin DVP camera connector, speaker header | `微雪 ESP32-S3 AUDIO Board` |
| 1 | OV2640 camera board, 24-pin, 0.5 mm FPC | 35.7 x 23.9 mm; connector orientation matches the audio board | `OV2640 24P 0.5mm FPC 微雪` |
| 1 | 4 ohm / 3 W speaker with pre-crimped 1.25 mm 2P plug | 40 mm maximum diameter, connector already fitted | `4欧3W 喇叭 1.25 2P 带线` |
| 1 | ESP32 DevKitC V4 | USB-C and pre-soldered headers | `ESP32 DevKitC V4 已焊排针 Type-C` |
| 1 | TB6612FNG motor-driver board | pre-soldered signal header, screw terminals, STBY exposed | `TB6612FNG 端子 已焊排针` |
| 1 | PCA9685 16-channel servo board | pre-soldered header and separate servo power terminal | `PCA9685 已焊排针 舵机板` |
| 1 | USB-A to USB-C power lead | 20-30 cm, rated 3 A or above | `USB A 转 Type C 20cm 3A` |

## Power and pre-made wiring

| Qty | Exact specification | Why it is required |
| --- | --- | --- |
| 1 | 2S 7.4 V, 1500 mAh or higher, >= 20C LiPo soft pack, XT30 output, <= 80 x 46 x 22 mm | Fits the printed tray and supplies the simultaneous servo/motor peak. |
| 1 | Matched 2S balance charger for that pack | Never charge a 2S LiPo from a 5 V USB charger. |
| 1 | 5 V / 10 A fixed buck converter, screw terminals | Feeds PCA9685 servo rail, ESP32 DevKitC and the audio board through USB-C. 3 A is not sufficient. |
| 1 | 6.0 V / 3 A fixed buck converter, screw terminals | Feeds only TB6612 `VM` and the two N20 motors. A 2S pack must not be connected directly to 6 V motors. |
| 1 | XT30 pre-made pigtail to stripped/tinned wire, 20 cm | Connects the battery to the fused power split without soldering. |
| 1 | 5 A inline automotive-style fuse holder and 5 A fuse | In series with battery positive before both buck converters. |
| 1 | Pre-crimped Dupont kit, 20 cm, male-to-female and female-to-female | For ESP32, PCA9685 and TB6612 signals. |
| 1 | WAGO 221-412 lever connectors, or a small screw-terminal power distribution block | Makes the battery/buck ground common without soldering. |

## Do not buy

- CoreS3, standalone ESP32-S3-WROOM modules, bare PCBs, or boards requiring
  header soldering.
- SG90 continuous rotation servos, 2 g aircraft servos, or MG90S 360-degree
  versions. They cannot position the head and arms.
- 18650 holders, unprotected loose cells, a 3 A 5 V buck, or an N20 motor
  marked 300 RPM or 12 V.
- TPU filament. The purchased rubber wheels are the correct tyre material.

## Seller confirmation message

Send this exact question to a seller when a dimension is not on the page:

> 请确认这款 N20 电机为 6V、100RPM、3mm D 型输出轴，电机本体 10x12mm、总长 34-36mm、轴长至少 9mm，并且堵转电流不超过 0.8A。请确认轮子外径 42mm、宽度不超过 19mm、孔为 3mm D 孔。请提供实物尺寸图。
