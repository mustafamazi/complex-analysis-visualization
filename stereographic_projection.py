"""
Visualization of the stereographic projection.

Riemann sphere: x1^2 + x2^2 + x3^2 = 1   (unit sphere)
Complex plane:  the plane x3 = 0, z = x + iy  <->  (x, y, 0)
North pole:     N = (0, 0, 1)

The line from N to z meets the sphere at exactly one point P other than N:

    P = ( 2x / (|z|^2 + 1),  2y / (|z|^2 + 1),  (|z|^2 - 1) / (|z|^2 + 1) )

Inverse map:  z = (X1 + i X2) / (1 - X3)

- |z| < 1  ->  P is in the southern hemisphere
- |z| = 1  ->  P = z (the equator stays fixed)
- |z| > 1  ->  P is in the northern hemisphere, and P -> N as |z| -> ∞

Re(z) and Im(z) can be changed with the sliders.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

N = np.array([0.0, 0.0, 1.0])
PLANE_LIM = 2.5


def z_to_sphere(z):
    """Map the complex number z to the point P on the Riemann sphere."""
    r2 = abs(z) ** 2
    return np.array([2 * z.real, 2 * z.imag, r2 - 1]) / (r2 + 1)


def sphere_to_z(P):
    """Map a point P (P != N) on the sphere to the complex plane."""
    return complex(P[0], P[1]) / (1 - P[2])


fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection="3d")
plt.subplots_adjust(bottom=0.18)

# Riemann sphere
u, v = np.mgrid[0:2 * np.pi:60j, 0:np.pi:30j]
ax.plot_surface(np.cos(u) * np.sin(v), np.sin(u) * np.sin(v), np.cos(v),
                color="skyblue", alpha=0.18, linewidth=0)
ax.plot_wireframe(np.cos(u) * np.sin(v), np.sin(u) * np.sin(v), np.cos(v),
                  color="steelblue", alpha=0.15, rstride=5, cstride=5)

# Complex plane (x3 = 0)
gx, gy = np.meshgrid(np.linspace(-PLANE_LIM, PLANE_LIM, 2),
                     np.linspace(-PLANE_LIM, PLANE_LIM, 2))
ax.plot_surface(gx, gy, np.zeros_like(gx), color="lightgray", alpha=0.25)
ax.plot([-PLANE_LIM, PLANE_LIM], [0, 0], [0, 0], color="gray", lw=0.8)
ax.plot([0, 0], [-PLANE_LIM, PLANE_LIM], [0, 0], color="gray", lw=0.8)
ax.text(PLANE_LIM, 0, 0, "  Re", color="gray")
ax.text(0, PLANE_LIM, 0, "  Im", color="gray")

# Equator = unit circle |z| = 1 (fixed by the projection)
t = np.linspace(0, 2 * np.pi, 200)
ax.plot(np.cos(t), np.sin(t), 0, color="green", lw=1.2, ls="--",
        label="equator / |z| = 1")

# North pole
ax.scatter(*N, color="black", s=60, depthshade=False)
ax.text(*(N + [0.05, 0.05, 0.08]), "N (0,0,1)", fontsize=11, weight="bold")

# Moving elements
line, = ax.plot([], [], [], color="purple", lw=1.5, label="line N → z")
drop, = ax.plot([], [], [], color="orange", lw=1, ls=":")
z_pt = ax.scatter([], [], [], color="red", s=60, depthshade=False, label="z (on the plane)")
p_pt = ax.scatter([], [], [], color="blue", s=60, depthshade=False, label="P (on the sphere)")
z_txt = ax.text(0, 0, 0, "", color="red", fontsize=11, weight="bold")
p_txt = ax.text(0, 0, 0, "", color="blue", fontsize=11, weight="bold")
info = fig.text(0.02, 0.92, "", fontsize=10, family="monospace")


def update(_=None):
    z = complex(s_re.val, s_im.val)
    P = z_to_sphere(z)
    zp = np.array([z.real, z.imag, 0.0])

    # L(s) = N + s (z - N):  s = 1 -> z,  s = 2/(|z|^2+1) -> P
    s_P = 2 / (abs(z) ** 2 + 1)
    s = np.linspace(0, max(1.0, s_P), 2)
    L = N[:, None] + (zp - N)[:, None] * s
    line.set_data_3d(L[0], L[1], L[2])

    # Vertical line from P down to the plane (P's shadow)
    drop.set_data_3d([P[0], P[0]], [P[1], P[1]], [P[2], 0])

    z_pt._offsets3d = ([zp[0]], [zp[1]], [zp[2]])
    p_pt._offsets3d = ([P[0]], [P[1]], [P[2]])
    z_txt.set_position_3d(zp + [0.08, 0.08, 0.05])
    z_txt.set_text("z")
    p_txt.set_position_3d(P + [0.08, 0.08, 0.05])
    p_txt.set_text("P")

    info.set_text(
        f"z = {z.real:+.2f} {z.imag:+.2f}i    |z| = {abs(z):.2f}\n"
        f"P = ({P[0]:+.3f}, {P[1]:+.3f}, {P[2]:+.3f})\n"
        f"inverse:    (X1 + iX2)/(1 - X3) = {sphere_to_z(P):.2f}"
    )
    fig.canvas.draw_idle()


ax_re = plt.axes([0.2, 0.08, 0.6, 0.03])
ax_im = plt.axes([0.2, 0.03, 0.6, 0.03])
s_re = Slider(ax_re, "Re(z)", -PLANE_LIM, PLANE_LIM, valinit=1.5)
s_im = Slider(ax_im, "Im(z)", -PLANE_LIM, PLANE_LIM, valinit=1.0)
s_re.on_changed(update)
s_im.on_changed(update)

ax.set_xlim(-PLANE_LIM, PLANE_LIM)
ax.set_ylim(-PLANE_LIM, PLANE_LIM)
ax.set_zlim(-1.2, 1.4)
ax.set_box_aspect((2 * PLANE_LIM, 2 * PLANE_LIM, 2.6), zoom=1.3)
ax.set_xlabel("x₁  (Re)")
ax.set_ylabel("x₂  (Im)")
ax.set_zlabel("x₃")
ax.set_title("Stereographic Projection: Riemann Sphere ↔ Complex Plane")
ax.view_init(elev=20, azim=-60)
ax.legend(loc="upper right", fontsize=9)

update()
plt.show()
