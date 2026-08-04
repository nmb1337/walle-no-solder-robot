# Hardware overview

Use [docs/BOM.md](docs/BOM.md) for the complete procurement specification and
[docs/ASSEMBLY.md](docs/ASSEMBLY.md) for the no-solder harness order.

The architecture has two controllers:

- ESP32 DevKitC V4 -> TB6612FNG -> two 6 V N20 motors and PCA9685 -> six
  MG90S 180-degree servos.
- Waveshare ESP32-S3-AUDIO-Board + OV2640 + 4 ohm speaker -> Wi-Fi voice and
  camera client for the Windows gateway.

Power starts at a fused 2S LiPo XT30 output. It splits into a `6.0 V / 3 A`
motor rail and an isolated `5 V / 10 A` servo/logic rail, with all grounds
common. The ESP32-S3 audio board receives the 5 V logic rail through USB-C.
No 6 V motor rail may enter an ESP32, PCA9685 logic pin or servo connector.
