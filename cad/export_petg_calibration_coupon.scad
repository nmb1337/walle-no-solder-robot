// A1 PETG coupon: 80 x 20 x 2 mm, no support. Measure thickness and bridging
// after cooling before making functional parts.
difference() {
    cube([80, 20, 2]);
    for (x = [10:10:70]) translate([x, 10, -1]) cylinder(d = 3.2, h = 4, $fn = 32);
}
