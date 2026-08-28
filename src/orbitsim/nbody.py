"""Generic point-mass N-body propagation using fixed-step RK4."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np

G_KM3_KG_S2 = 6.67430e-20

@dataclass(frozen=True)
class Body:
    name: str
    mass_kg: float

@dataclass(frozen=True)
class NBodyResult:
    times_s: np.ndarray
    positions_km: np.ndarray  # (samples, bodies, 3)
    velocities_km_s: np.ndarray  # (samples, bodies, 3)


def _accelerations(positions_km: np.ndarray, bodies: tuple[Body, ...]) -> np.ndarray:
    r = np.asarray(positions_km, dtype=float)
    n = len(bodies)
    a = np.zeros_like(r)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            dr = r[j] - r[i]
            d = np.linalg.norm(dr)
            if d < 1e-9:
                raise ValueError("N-body propagation encountered a collision/near-collision")
            a[i] += G_KM3_KG_S2 * bodies[j].mass_kg * dr / d**3
    return a


def propagate_nbody(
    bodies: tuple[Body, ...],
    positions0_km: np.ndarray,
    velocities0_km_s: np.ndarray,
    duration_s: float,
    dt_s: float = 3600.0,
) -> NBodyResult:
    """Propagate mutually gravitating point masses with classical RK4."""
    if len(bodies) < 2:
        raise ValueError("at least two bodies are required")
    if duration_s <= 0 or dt_s <= 0:
        raise ValueError("duration_s and dt_s must be positive")
    positions = np.asarray(positions0_km, dtype=float).copy()
    velocities = np.asarray(velocities0_km_s, dtype=float).copy()
    if positions.shape != (len(bodies), 3) or velocities.shape != (len(bodies), 3):
        raise ValueError("positions0_km and velocities0_km_s must have shape (N, 3)")
    if any(body.mass_kg <= 0 for body in bodies):
        raise ValueError("body masses must be positive")

    n_steps = int(np.ceil(duration_s / dt_s))
    times = np.empty(n_steps + 1)
    pos_hist = np.empty((n_steps + 1, len(bodies), 3))
    vel_hist = np.empty_like(pos_hist)
    times[0] = 0.0
    pos_hist[0] = positions
    vel_hist[0] = velocities

    def deriv(p: np.ndarray, v: np.ndarray):
        return v, _accelerations(p, bodies)

    for k in range(n_steps):
        h = min(dt_s, duration_s - times[k])
        if h <= 0:
            times = times[: k + 1]
            pos_hist = pos_hist[: k + 1]
            vel_hist = vel_hist[: k + 1]
            break
        k1r, k1v = deriv(positions, velocities)
        k2r, k2v = deriv(positions + 0.5*h*k1r, velocities + 0.5*h*k1v)
        k3r, k3v = deriv(positions + 0.5*h*k2r, velocities + 0.5*h*k2v)
        k4r, k4v = deriv(positions + h*k3r, velocities + h*k3v)
        positions = positions + h*(k1r + 2*k2r + 2*k3r + k4r)/6
        velocities = velocities + h*(k1v + 2*k2v + 2*k3v + k4v)/6
        times[k + 1] = times[k] + h
        pos_hist[k + 1] = positions
        vel_hist[k + 1] = velocities
    return NBodyResult(times, pos_hist, vel_hist)


def sun_earth_moon_demo(duration_days: float = 365.25, dt_hours: float = 6.0) -> NBodyResult:
    """Educational Sun-Earth-Moon point-mass example in a heliocentric frame."""
    sun = Body("Sun", 1.98847e30)
    earth = Body("Earth", 5.9722e24)
    moon = Body("Moon", 7.342e22)
    bodies = (sun, earth, moon)

    au = 149_597_870.7
    earth_orbit_speed = np.sqrt(G_KM3_KG_S2 * sun.mass_kg / au)
    moon_distance = 384_400.0
    moon_relative_speed = np.sqrt(G_KM3_KG_S2 * earth.mass_kg / moon_distance)

    positions = np.array([
        [0.0, 0.0, 0.0],
        [au, 0.0, 0.0],
        [au + moon_distance, 0.0, 0.0],
    ])
    velocities = np.array([
        [0.0, -earth.mass_kg * earth_orbit_speed / sun.mass_kg, 0.0],
        [0.0, earth_orbit_speed, 0.0],
        [0.0, earth_orbit_speed + moon_relative_speed, 0.0],
    ])
    return propagate_nbody(bodies, positions, velocities, duration_days * 86400.0, dt_hours * 3600.0)
