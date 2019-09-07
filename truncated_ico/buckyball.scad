/*
 *  backy ball fractal
 *  (c) 2015. 10. 30 by SASAKI, Taroh
 */

fdepth = 1;
childsc = .175; // touches edge at 0.171
swhex  = 1;     // for dual color printing
swpent = 1;
 
// Cartesian coordinates (from wikipedia):
//  Cartesian coordinates for the vertices of a 
//  truncated icosahedron centered at the origin are all even
//  permutations of:
//      (0, ±1, ±3ϕ)
//      (±2, ±(1+2ϕ), ±ϕ)
//      (±1, ±(2+ϕ), ±2ϕ)
//  where ϕ = (1 + √5) / 2 is the golden mean.
//  Radius squared equal to 9ϕ + 10
//  (radius ~= 4.956037)
//  The edges have length 2.
//
//  rotate 20.90516 (around y axis) degree afterwards to 
//  fit hexagon on
//  x-y plane.

phi = (1 + sqrt(5)) / 2;

pp1 = [0, 1, 3 * phi];
pp2 = [phi, 2, 1 + 2 * phi];
pp3 = [2 * phi, 1, 2 + phi];
po = [0, 0, 0];

// 12 x hex ddh around +/- z axis (0 <= x, ccw)
ddh6 = pp1;
ddh5 = pp2;
ddh4 = pp3;
ddh3 = [ddh4[0], -ddh4[1], ddh4[2]];
ddh2 = [ddh5[0], -ddh5[1], ddh5[2]];
ddh1 = [ddh6[0], -ddh6[1], ddh6[2]];

// 12 x pent ddp right/under ddh 
ddp1 = [pp1[2], pp1[0], pp1[1]];
ddp2 = [pp2[2], pp2[0], pp2[1]];
ddp3 = ddh4;
ddp4 = [ddp3[0], -ddp3[1], ddp3[2]];
ddp5 = [ddp2[0], -ddp2[1], ddp2[2]];

// 8 x hex och at corner (0 <= x, 0 <= y, 0 <= z)
och1 = ddh5;
och2 = ddh4;
och3 = ddp2;
och4 = [pp3[2], pp3[0], pp3[1]];
och5 = [pp2[1], pp2[2], pp2[0]];
och6 = [pp3[1], pp3[2], pp3[0]];


recbucky(0);


function negx(vec) = [-vec[0],  vec[1],  vec[2]];
function negy(vec) = [ vec[0], -vec[1],  vec[2]];
function negz(vec) = [ vec[0],  vec[1], -vec[2]];
function perm(vec) = [ vec[2], vec[0], vec[1]];

module
recbucky(depth)
{
    if (depth == fdepth) {
        drawbucky();
    } else {
// note: duplicate codes because OpenSCAD
//   don't allow child's child recursive, while
//   child recursive is available.
        
// (0 < x, 0 < y, 0 < z)
        drawchild(depth, och1);
        drawchild(depth, och2);
        drawchild(depth, och3);
        drawchild(depth, och4);
        drawchild(depth, och5);
        drawchild(depth, och6);
// (x < 0, 0 < y, 0 < z)
        drawchild(depth, negx(och1));
        drawchild(depth, negx(och2));
        drawchild(depth, negx(och3));
        drawchild(depth, negx(och4));
        drawchild(depth, negx(och5));
        drawchild(depth, negx(och6));
// (0 < x, y < 0, 0 < z)
        drawchild(depth, negy(och1));
        drawchild(depth, negy(och2));
        drawchild(depth, negy(och3));
        drawchild(depth, negy(och4));
        drawchild(depth, negy(och5));
        drawchild(depth, negy(och6));
// (0 < x, y < 0, 0 < z)
        drawchild(depth, negy(negx(och1)));
        drawchild(depth, negy(negx(och2)));
        drawchild(depth, negy(negx(och3)));
        drawchild(depth, negy(negx(och4)));
        drawchild(depth, negy(negx(och5)));
        drawchild(depth, negy(negx(och6)));

// (0 < x, 0 < y, z < 0)
        drawchild(depth, negz(och1));
        drawchild(depth, negz(och2));
        drawchild(depth, negz(och3));
        drawchild(depth, negz(och4));
        drawchild(depth, negz(och5));
        drawchild(depth, negz(och6));
// (x < 0, 0 < y, z < 0)
        drawchild(depth, negz(negx(och1)));
        drawchild(depth, negz(negx(och2)));
        drawchild(depth, negz(negx(och3)));
        drawchild(depth, negz(negx(och4)));
        drawchild(depth, negz(negx(och5)));
        drawchild(depth, negz(negx(och6)));
// (0 < x, y < 0, z < 0)
        drawchild(depth, negz(negy(och1)));
        drawchild(depth, negz(negy(och2)));
        drawchild(depth, negz(negy(och3)));
        drawchild(depth, negz(negy(och4)));
        drawchild(depth, negz(negy(och5)));
        drawchild(depth, negz(negy(och6)));
// (0 < x, y < 0, z < 0)
        drawchild(depth, negz(negy(negx(och1))));
        drawchild(depth, negz(negy(negx(och2))));
        drawchild(depth, negz(negy(negx(och3))));
        drawchild(depth, negz(negy(negx(och4))));
        drawchild(depth, negz(negy(negx(och5))));
        drawchild(depth, negz(negy(negx(och6))));
        
// around z axis
        drawchild(depth, pp1);
        drawchild(depth, negy(pp1));
        drawchild(depth, negz(pp1));
        drawchild(depth, negz(negy(pp1)));
// around x axis
        drawchild(depth, perm(pp1));
        drawchild(depth, negz(perm(pp1)));
        drawchild(depth, negx(perm(pp1)));
        drawchild(depth, negx(negz(perm(pp1))));
// around y axis
        drawchild(depth, perm(perm(pp1)));
        drawchild(depth, negx(perm(perm(pp1))));
        drawchild(depth, negy(perm(perm(pp1))));
        drawchild(depth, negy(negx(perm(perm(pp1)))));
    }
}


module
drawchild(depth, vec) {
    translate(vec * (1 - childsc)) {
        scale(childsc) {
            recbucky(depth + 1);
        }
    }
}


module
drawbucky()
{
    drawzxdd();
    rotate([0, 90, 0]) {
        rotate([90, 0, 0]) {
            drawzxdd();
        }
    }
    rotate([90, 0, 0]) {
        rotate([0, 90, 0]) {
            drawzxdd();
        }
    }
    drawyxoc();
    mirror([0, 0, 1]) {
        drawyxoc();
    }
    cube(size = [.1, .1, .1], center = true);
    // dummy cube to fill crack at (0, 0, 0) by
    // OpenSCAD error???
}


module
drawdd() {
    drawhex(ddh1, ddh2, ddh3, ddh4, ddh5, ddh6);
    drawpent(ddp1, ddp2, ddp3, ddp4, ddp5);
}

module
drawxdd() { // y-z plane mirror
    drawdd();
    mirror([1, 0, 0]) {
        drawdd();
    }
}

module
drawzxdd()  // x-y plane mirror
{
    drawxdd();
    mirror([0, 0, 1]) {
        drawxdd();
    }
}


module
drawoc()
{
    drawhex(och1, och2, och3, och4, och5, och6);
}

module
drawxoc() // y-z plane mirror
{
    drawoc();
    mirror([1, 0, 0]) {
        drawoc();
    }
}

module
drawyxoc() // x-z plane mirror
{
    drawxoc();
    mirror([0, 1, 0]) {
        drawxoc();
    }
}


module
drawhex(p1, p2, p3, p4, p5, p6)
{
  if (swhex == 1) {
    polyhedron(points = [po, p1, p2, p3, p4, p5, p6],
        faces = [[1, 2, 3, 4, 5, 6],
            [0, 2, 1], [0, 3, 2], [0, 4, 3],
            [0, 5, 4], [0, 6, 5], [0, 1, 6]]);
  }
}

module
drawpent(p1, p2, p3, p4, p5)
{
  if (swpent == 1) {
    polyhedron(points = [po, p1, p2, p3, p4, p5],
        faces = [[1, 2, 3, 4, 5],
            [0, 2, 1], [0, 3, 2], [0, 4, 3],
            [0, 5, 4], [0, 1, 5]]);
  }
}
    
