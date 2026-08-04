// WALLE no-solder medium robot, millimetres.
// Target hardware: 43 mm N20 rubber wheels, MG90S 180-degree servos,
// Waveshare ESP32-S3-Touch-LCD-3.5-C (95.11 x 63.67 x 14.10 mm case,
// with OV5640 camera) and MG90S servos. Every printed part fits a Bambu A1.

$fn = 64;

body_w = 184;
body_d = 118;
body_h = 100;
head_w = 182;
head_d = 90;
head_h = 76;
wall = 3;
clearance = 0.8;

drive_wheel_d = 43;
drive_wheel_w = 19;
drive_axle_d = 3;               // N20 3 mm D-shaft
wheel_center_z = drive_wheel_d / 2 + 4;
motor_axis_z = wheel_center_z;  // N20 shaft and wheel bore must be coaxial

mg90s_w = 22.8;
mg90s_d = 12.2;
mg90s_h = 28.5;

touch_lcd_w = 95.11;            // official case outline, mm
touch_lcd_d = 63.67;
touch_lcd_h = 14.10;
camera_pcb_w = 28;               // OV5640 module envelope; verify seller sample
camera_pcb_h = 28;

// 2S 1800 mAh pack envelope. Smaller packs use foam and hook-and-loop strap.
battery_bay_w = 82;
battery_bay_d = 48;
battery_bay_h = 24;

part = "none";

module rounded_box(w, d, h, r = 8) {
    linear_extrude(height = h, center = true)
        hull()
            for (x = [-w / 2 + r, w / 2 - r])
                for (y = [-d / 2 + r, d / 2 - r])
                    translate([x, y]) circle(r = r);
}

module m3_hole(h = 20) { cylinder(d = 3.4, h = h, center = true); }
module m2_hole(h = 20) { cylinder(d = 2.4, h = h, center = true); }

module base_plate() {
    difference() {
        rounded_box(178, 112, 5, 10);
        for (x = [-76, 76], y = [-43, 43])
            translate([x, y, 0]) m3_hole();
        // N20 motor-clamp pairs. Clamp centres are x = +/-80, y = 0.
        for (x = [-80, 80], y = [-9, 9])
            translate([x, y, 0]) m3_hole();
        // Rear ball-caster plate. M2 slots allow small seller variations.
        for (x = [-6, 6])
            translate([x, -43, 0]) m2_hole();
        // Hook-and-loop slots for battery and cable restraint.
        for (y = [-22, 22])
            translate([0, y, 0]) cube([28, 4, 10], center = true);
    }
}

module body_shell() {
    difference() {
        translate([0, 0, body_h / 2]) rounded_box(body_w, body_d, body_h, 12);
        // Open top, 6 mm bottom, 4 mm rear wall. Electronics insert from above.
        translate([0, -3, body_h / 2 + 5]) rounded_box(body_w - 8, body_d - 8, body_h, 9);
        // Clearance for two real 43 mm rubber wheels.
        for (side = [-1, 1])
            translate([side * (body_w / 2 + 2), 0, wheel_center_z])
                rotate([0, 90, 0]) cylinder(d = drive_wheel_d + 4, h = 16, center = true);
        // Match the base plate's four M3 body-fastening holes.
        for (x = [-76, 76], y = [-43, 43])
            translate([x, y, 3]) m3_hole(16);
    }
}

// Cosmetic side cover: it creates the WALL-E tracked appearance while the
// bought rubber wheel remains exposed through the 46 mm opening.
module track_cover() {
    difference() {
        rotate([0, 90, 0])
            linear_extrude(height = 5, center = true)
                difference() {
                    hull() {
                        translate([0, -32]) circle(d = 58);
                        translate([0, 32]) circle(d = 58);
                    }
                    circle(d = drive_wheel_d + 4);
                }
        // Two M3 mounting holes along the long axis.
        for (y = [-43, 43])
            translate([0, y, 0]) rotate([0, 90, 0]) m3_hole(12);
    }
}

module n20_motor_clamp() {
    difference() {
        // A raised cradle: base sits at Z=0 and the N20 shaft shares the
        // 43 mm wheel centreline in this chassis.
        translate([0, 0, motor_axis_z]) rounded_box(42, 28, 50, 3);
        // N20 motor body and gearbox, axis along X. Use two small cable ties.
        translate([0, 0, motor_axis_z]) cube([38.5, 13.4, 11.4], center = true);
        translate([0, 0, motor_axis_z + 9]) cube([44, 18, 12], center = true);
        // Exit for either left or right 3 mm D-shaft; the printed clamp is
        // symmetric so one STL serves both sides of the chassis.
        translate([0, 0, motor_axis_z]) rotate([0, 90, 0]) cylinder(d = 5, h = 48, center = true);
        for (x = [-13, 13])
            translate([x, 0, motor_axis_z]) cube([3.5, 32, 4], center = true);
        // The base has matching M3 holes at x=+/-80, y=+/-9.
        for (y = [-9, 9])
            translate([0, y, 5]) m3_hole(12);
    }
}

module battery_tray() {
    difference() {
        rounded_box(battery_bay_w + 8, battery_bay_d + 8, battery_bay_h + 6, 5);
        translate([0, 0, 3]) rounded_box(battery_bay_w, battery_bay_d, battery_bay_h + 8, 3);
        for (y = [-15, 15])
            translate([0, y, 0]) cube([32, 4, 40], center = true);
    }
}

module electronics_deck() {
    difference() {
        rounded_box(174, 106, 3, 7);
        for (x = [-78, 78], y = [-44, 44])
            translate([x, y, 0]) m3_hole();
        // Universal tie-down slots instead of vendor-specific hole patterns.
        for (x = [-55, -25, 25, 55])
            translate([x, 0, 0]) cube([3.5, 34, 10], center = true);
    }
}

module head_shell() {
    difference() {
        translate([0, 0, head_h / 2]) rounded_box(head_w, head_d, head_h, 10);
        // Face is a separate panel; this leaves the front open for service.
        translate([0, -3, head_h / 2 + 3]) rounded_box(head_w - 8, head_d, head_h - 6, 7);
    }
}

module face_plate() {
    difference() {
        translate([0, 0, 36]) rounded_box(174, 5, 70, 8);
        for (x = [-44, 44])
            translate([x, 0, 43]) rotate([90, 0, 0]) cylinder(d = 40, h = 12, center = true);
        // Speaker grille: three rows of 4 mm holes below the eyes.
        for (x = [-24 : 8 : 24], z = [10 : 8 : 26])
            translate([x, 0, z]) rotate([90, 0, 0]) cylinder(d = 4, h = 12, center = true);
        for (x = [-76, 76])
            translate([x, 0, 8]) rotate([90, 0, 0]) m3_hole(12);
    }
}

module eye_ring() {
    difference() {
        rotate([90, 0, 0]) cylinder(d = 48, h = 8, center = true);
        rotate([90, 0, 0]) cylinder(d = 38, h = 12, center = true);
    }
}

// Holds the OV5640 camera board behind the right eye. The 28 x 28 mm cavity
// leaves 1 mm radial clearance for the seller's supplied camera carrier.
module ov5640_camera_mount() {
    difference() {
        rounded_box(38, 10, 38, 3);
        cube([camera_pcb_w + 2, 14, camera_pcb_h + 2], center = true);
        rotate([90, 0, 0]) cylinder(d = 14, h = 16, center = true);
        for (x = [-14, 14])
            translate([x, 0, -14]) rotate([90, 0, 0]) m3_hole(16);
    }
}

// Rectangular cradle for the official Waveshare case. The board slides in
// from the rear; the 1 mm perimeter allowance avoids a force fit.
module touch_lcd_cradle() {
    difference() {
        rounded_box(touch_lcd_w + 8, touch_lcd_d + 8, touch_lcd_h + 8, 5);
        translate([0, 0, 3])
            rounded_box(touch_lcd_w + 2, touch_lcd_d + 2, touch_lcd_h + 8, 4);
        translate([0, 0, 9]) cube([56, 16, 12], center = true); // cable access
        for (x = [-46, 46], y = [-30, 30])
            translate([x, y, 0]) m3_hole(20);
    }
}

// Compatibility aliases for earlier V2 file names.
module ov2640_camera_mount() { ov5640_camera_mount(); }
module audio_core_cradle() { touch_lcd_cradle(); }

module mg90s_servo_cradle() {
    difference() {
        rounded_box(31, 22, 33, 3);
        translate([0, 0, 1]) cube([mg90s_w + 0.9, mg90s_d + 0.9, mg90s_h + 1], center = true);
        for (x = [-12, 12])
            translate([x, 0, -12]) m3_hole(8);
    }
}

module shoulder_mount() {
    difference() {
        rounded_box(40, 30, 38, 4);
        translate([0, 0, 1]) cube([mg90s_w + 1, mg90s_d + 1, mg90s_h + 2], center = true);
        rotate([90, 0, 0]) cylinder(d = 8, h = 40, center = true);
        for (x = [-15, 15]) translate([x, 0, -14]) m3_hole(10);
    }
}

module arm_link_upper() {
    difference() {
        hull() {
            translate([-24, 0, 0]) cylinder(d = 18, h = 12, center = true);
            translate([24, 0, 0]) cylinder(d = 18, h = 12, center = true);
        }
        for (x = [-24, 24]) translate([x, 0, 0]) cylinder(d = 3.4, h = 20, center = true);
    }
}

module arm_link_lower() {
    difference() {
        hull() {
            translate([-20, 0, 0]) cylinder(d = 16, h = 10, center = true);
            translate([20, 0, 0]) cylinder(d = 16, h = 10, center = true);
        }
        for (x = [-20, 20]) translate([x, 0, 0]) cylinder(d = 3.4, h = 18, center = true);
    }
}

module head_servo_adapter() {
    difference() {
        rounded_box(60, 34, 5, 4);
        for (x = [-22, 22], y = [-10, 10]) translate([x, y, 0]) m3_hole();
        rotate([0, 0, 0]) cylinder(d = 8, h = 12, center = true);
    }
}

// Uses the supplied MG90S cross horn. The two central M2 holes match the
// short arm of the common 9 g servo horn; the outer M3 holes join the printed
// arm/head link. Confirm the supplied horn hole pitch during the first dry fit.
module mg90s_horn_adapter() {
    difference() {
        rounded_box(26, 20, 4, 3);
        for (x = [-2.5, 2.5]) translate([x, 0, 0]) m2_hole(10);
        for (x = [-10, 10]) translate([x, 0, 0]) m3_hole(10);
    }
}

// Flat adapter below the base plate for a bought <=20 x 20 x 16 mm ball
// caster. Its M2 slots accept a 12 mm nominal mounting pitch.
module ball_caster_plate() {
    difference() {
        rounded_box(30, 24, 4, 4);
        for (x = [-6, 6]) translate([x, 0, 0]) m2_hole(10);
        for (x = [-8, 8]) translate([x, -4, 0]) m2_hole(10);
    }
}

module assembly_preview() {
    color("#b98320") translate([0, 0, 0]) base_plate();
    color("#d7a72a") translate([0, 0, 3]) body_shell();
    for (side = [-1, 1]) {
        // N20 is mounted with its shaft along X, 25 mm above the base plane.
        // The bought wheel's 3 mm D-bore shares this exact centreline.
        color("#707070") translate([side * 80, 0, 0]) n20_motor_clamp();
        color("#242424") translate([side * 99, 0, wheel_center_z])
            rotate([0, 90, 0]) cylinder(d = drive_wheel_d, h = drive_wheel_w, center = true);
        color("#3b3b3b") translate([side * 108, 0, wheel_center_z]) track_cover();
    }
    color("#d7a72a") translate([0, -8, 108]) head_shell();
    color("#202020") translate([0, -56, 108]) face_plate();
    for (x = [-44, 44]) color("#202020") translate([x, -61, 151]) eye_ring();
}

if (part == "base_plate") base_plate();
if (part == "body_shell") body_shell();
if (part == "track_cover") track_cover();
if (part == "n20_motor_clamp") n20_motor_clamp();
if (part == "battery_tray") battery_tray();
if (part == "electronics_deck") electronics_deck();
if (part == "head_shell") head_shell();
if (part == "face_plate") face_plate();
if (part == "eye_ring") eye_ring();
if (part == "ov2640_camera_mount") ov2640_camera_mount();
if (part == "ov5640_camera_mount") ov5640_camera_mount();
if (part == "touch_lcd_cradle") touch_lcd_cradle();
if (part == "audio_core_cradle") audio_core_cradle();
if (part == "mg90s_servo_cradle") mg90s_servo_cradle();
if (part == "shoulder_mount") shoulder_mount();
if (part == "arm_link_upper") arm_link_upper();
if (part == "arm_link_lower") arm_link_lower();
if (part == "head_servo_adapter") head_servo_adapter();
if (part == "mg90s_horn_adapter") mg90s_horn_adapter();
if (part == "ball_caster_plate") ball_caster_plate();
if (part == "assembly_preview") assembly_preview();
