// Printable 1:1 physical alignment gauge. The horizontal line through the
// 3 mm D-bore target is exactly motor_axis_z above the underside.
motor_axis_z = 25.5;
difference() {
    cube([72, 40, motor_axis_z + 8], center = false);
    translate([0, 0, motor_axis_z]) rotate([0, 90, 0]) cylinder(d = 3.4, h = 90, center = true);
    for (y = [11, 29]) translate([36, y, 5]) cylinder(d = 3.4, h = 16, center = true);
}
