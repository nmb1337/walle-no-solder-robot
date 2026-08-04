# Motion controller

`esp32_walle_controller.ino` runs on the pre-soldered ESP32 DevKitC V4. It
polls the Windows gateway every 250 ms, drives a TB6612FNG motor driver and a
PCA9685 servo board, and stops both motors after one second without a command.

## Exact connections

| ESP32 pin | TB6612FNG |
| --- | --- |
| GPIO 25 | AIN1 |
| GPIO 26 | AIN2 |
| GPIO 27 | PWMA |
| GPIO 32 | BIN1 |
| GPIO 33 | BIN2 |
| GPIO 14 | PWMB |
| GPIO 13 | STBY |
| 3.3 V | VCC |
| GND | GND |

PCA9685: ESP32 `GPIO 21 -> SDA`, `GPIO 22 -> SCL`, common GND, and a separate
regulated `5 V / 8 A or higher` rail on its servo power terminal. Motors use
the protected 2S battery at `VM`; the ESP32 and PCA9685 must share GND with
that battery but never draw servo current through the ESP32 USB port.

The sketch supports Arduino-ESP32 2.x and 3.x LEDC APIs. Gateway events use
ASCII values (`left`, `right`, `center`, `up`, `down`, `raise`, `stow`) so the
firmware is not affected by serial or source-file Chinese encoding.

Before fitting wheels or arms, power the controller from USB, verify all six
servo directions, then test each motor with the robot raised off the table.
