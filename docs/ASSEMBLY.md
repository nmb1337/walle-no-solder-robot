# No-solder assembly guide

Do not start with the body shell. Build in the order below and stop whenever a
fit check fails. The battery is connected only during the final electrical
test.

## 1. Print and measure the fit set

Print the V2 parts in PETG, 0.20 mm layer height, four walls and 30% gyroid:

1. `walle_n20_motor_clamp.stl` x2
2. `walle_battery_tray.stl` x1
3. `walle_audio_core_cradle.stl` x1
4. `walle_ov2640_camera_mount.stl` x1
5. `walle_mg90s_servo_cradle.stl` x2 and `walle_shoulder_mount.stl` x2
6. `walle_mg90s_horn_adapter.stl` x6 and `walle_ball_caster_plate.stl` x1
7. `walle_base_plate.stl` x1

Verify with calipers: N20 body must enter the clamp without force; the battery
must have at least 1 mm free space on each side; the audio board must sit in
its cradle with the USB-C and FPC connector accessible. A failed fit means
change the CAD parameter, re-export only that part, and repeat.

## 2. Prepare the mechanical subassemblies

1. Insert each MG90S into its printed cradle with the output shaft facing the
   printed arm/head adapter. Do not tighten the horn-centre screw yet.
2. Connect the supplied servo cross horn to its servo using the supplied centre
   screw. Attach the printed arm adapter to the horn with M2 x 6 screws and M2
   nuts; never drill the servo shaft or glue a horn permanently.
3. Bolt the base plate to the body with four M3 x 14 screws. The body floor
   and base mounting holes must be aligned before electronics are installed.
4. Put each N20 clamp on the base's outer M3 pair: clamp centres are
   `x = -80 mm` and `x = +80 mm`, with the two holes `18 mm` apart along Y.
   Use M3 x 10 screws and lock nuts. Fit the rubber wheels after the motors.
   Each wheel must be fully seated on the 3 mm D shaft, turn freely by hand,
   and not rub the PETG side cover.
5. Fit the rear ball caster last. With the robot on a flat table, both drive
   wheels and the caster must touch the surface; the body/base must be at
   least 3 mm above the table.

## 3. Make the power harness with pre-made parts

1. Battery XT30 positive -> 5 A fuse -> lever/screw-terminal distribution.
2. Distribution -> 5 V / 10 A buck input and 6 V / 3 A buck input.
3. 5 V buck -> PCA9685 servo power terminal, ESP32 DevKitC 5 V/VIN, and the
   ESP32-S3 audio board through its USB-C lead.
4. 6 V buck -> TB6612 `VM` and `GND` only.
5. Join every ground: battery, both buck converters, TB6612, ESP32, PCA9685
   and audio board. Do not connect the 6 V motor rail to any ESP32 pin.

Leave the battery unplugged until the multimeter check in the next section.

## 4. Signal wiring and bench test

Use the pin map in `firmware/README.md`. Power only from USB initially.

1. Upload the motor-controller firmware after filling Wi-Fi name, Wi-Fi
   password and the gateway LAN address.
2. With wheels off the ground, issue `forward`, `back`, `left`, `right`, then
   `stop` from the web UI. The one-second watchdog must stop both motors.
3. Power PCA9685 from the 5 V buck and test every servo independently before
   attaching the head/arms. Adjust the neutral angle in firmware only after
   confirming the safe physical range.
4. Connect the OV2640 FPC cable with power off. Then install the ESP32-S3
   audio board, speaker and USB-C power lead. Take one camera snapshot before
   enabling automatic screenshots.

## 5. Close the robot only after these tests pass

Install the electronic deck, secure wires with reusable cable ties, then fit
the head, arms, face panel and track covers. Keep the battery accessible and
do not pinch the camera FPC or speaker lead.

For real audio, configure an authorised STT/TTS API profile in the gateway.
The robot never stores API keys in either ESP32 firmware.
