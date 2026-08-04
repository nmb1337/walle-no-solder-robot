# Engineering validation

## Verified by source and generated STL

| Check | Result | Evidence |
| --- | --- | --- |
| A1 build volume | Pass | All V2 STLs are <= 256 mm; largest body is 184 x 118 x 100 mm. |
| Battery cavity | Conditional | Tray inner envelope is 82 x 48 x 24 mm; buy pack <= 80 x 46 x 22 mm. |
| Camera | Pass by envelope | Mount cavity is 36.9 x 25.1 mm for a 35.7 x 23.9 mm board. |
| Audio board | Pass by envelope | Cradle has 0.8 mm radial assembly allowance for the 58 mm board. |
| Servos | Conditional | MG90S envelope is modelled. Horn adapter and real horn alignment need a dry fit. |
| Motor driver | Conditional | TB6612 is valid only when N20 stall current is <= 0.8 A. |
| Power | Pass after correction | Separate 6 V motor and 5 V / 10 A servo rails prevent N20 over-voltage and servo brownout. |
| Drive stability | Conditional | A rear 15 mm ball caster is mandatory; do not run a two-contact-point chassis. |

## Required physical gates

The CAD cannot prove a seller's unlabelled shaft length, wheel width, battery
dimensions, or servo horn moulding. The project is therefore **not cleared for
full-shell printing** until these gates are checked:

1. Seller supplies N20 and wheel size drawings matching `docs/BOM.md`.
2. First motor clamp, wheel, battery tray, camera mount and audio cradle pass
   a no-force dry fit.
3. The mounted base clears the floor by at least 3 mm on all three contact
   points.
4. Measured buck outputs are 5.0 V and 6.0 V before connecting electronics.
5. All six servos sweep their intended range without an arm/head collision.
6. The motor watchdog stops the wheels after a one-second command loss.

Only after all six gates pass may the body, head and cosmetic covers be sent to
the A1. This is the boundary between a dimensionally reviewed design and a
physically validated robot.
