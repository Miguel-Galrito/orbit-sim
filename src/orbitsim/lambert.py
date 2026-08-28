"""Universal-variable Lambert solver for two-point, two-body transfers."""
from __future__ import annotations
import numpy as np
from .constants import MU_EARTH_KM3_S2


def _stumpff_c2(z: float) -> float:
    if z > 1e-8: return (1-np.cos(np.sqrt(z)))/z
    if z < -1e-8: return (np.cosh(np.sqrt(-z))-1)/(-z)
    return 0.5


def _stumpff_c3(z: float) -> float:
    if z > 1e-8: return (np.sqrt(z)-np.sin(np.sqrt(z)))/z**1.5
    if z < -1e-8: return (np.sinh(np.sqrt(-z))-np.sqrt(-z))/(-z)**1.5
    return 1/6


def lambert_universal(r1_km: np.ndarray, r2_km: np.ndarray, tof_s: float, mu: float = MU_EARTH_KM3_S2, prograde: bool = True) -> tuple[np.ndarray, np.ndarray]:
    """Solve the zero-revolution Lambert problem using universal variables."""
    r1 = np.asarray(r1_km, float); r2 = np.asarray(r2_km, float)
    if r1.shape != (3,) or r2.shape != (3,): raise ValueError("r1_km and r2_km must be length-3 vectors")
    if tof_s <= 0: raise ValueError("tof_s must be positive")
    r1m, r2m = np.linalg.norm(r1), np.linalg.norm(r2)
    cos_dtheta = np.clip(np.dot(r1, r2)/(r1m*r2m), -1.0, 1.0)
    cross = np.cross(r1, r2); sin_mag = np.linalg.norm(cross)/(r1m*r2m)
    sin_dtheta = sin_mag if (cross[2] >= 0) == prograde else -sin_mag
    dtheta = np.arctan2(sin_dtheta, cos_dtheta)
    A = np.sin(dtheta)*np.sqrt(r1m*r2m/(1-np.cos(dtheta)))
    if abs(A) < 1e-12: raise ValueError("Geometry is singular for 0/180 degree transfer")

    def y(z: float) -> float:
        c2, c3 = _stumpff_c2(z), _stumpff_c3(z)
        if c2 <= 0: return np.nan
        return r1m+r2m + A*(z*c3-1)/np.sqrt(c2)

    def F(z: float) -> float:
        c2, c3 = _stumpff_c2(z), _stumpff_c3(z); yz = y(z)
        if not np.isfinite(yz) or yz < 0: return np.nan
        return (yz/c2)**1.5*c3 + A*np.sqrt(yz) - np.sqrt(mu)*tof_s

    grid = np.linspace(-4*np.pi**2, 4*np.pi**2, 801); bracket = None; prev_z = prev_f = None
    for z in grid:
        fz = F(float(z))
        if not np.isfinite(fz): continue
        if prev_f is not None and fz*prev_f <= 0:
            bracket = (prev_z, float(z)); break
        prev_z, prev_f = float(z), fz
    if bracket is None: raise ValueError("No zero-revolution Lambert solution found for this geometry and time of flight")
    lo, hi = bracket
    for _ in range(200):
        z = 0.5*(lo+hi); fz = F(z)
        if not np.isfinite(fz): lo = z; continue
        if abs(fz) < 1e-8: break
        flo = F(lo)
        if np.isfinite(flo) and flo*fz <= 0: hi = z
        else: lo = z
    yz = y(z); f = 1-yz/r1m; g = A*np.sqrt(yz/mu); gdot = 1-yz/r2m
    if abs(g) < 1e-12: raise ValueError("Lambert solution is numerically singular")
    return (r2-f*r1)/g, (gdot*r2-r1)/g
