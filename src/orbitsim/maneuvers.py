"""Analytical impulsive maneuver and transfer-design utilities."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from .constants import MU_EARTH_KM3_S2

@dataclass(frozen=True)
class HohmannTransfer:
    r1_km: float; r2_km: float; delta_v1_km_s: float; delta_v2_km_s: float; total_delta_v_km_s: float; transfer_time_s: float

def _positive(value: float, name: str) -> None:
    if value <= 0: raise ValueError(f"{name} must be positive")

def hohmann_transfer(r1_km: float, r2_km: float, mu: float = MU_EARTH_KM3_S2) -> HohmannTransfer:
    _positive(r1_km, "r1_km"); _positive(r2_km, "r2_km")
    if np.isclose(r1_km, r2_km): raise ValueError("radii must be distinct")
    a_t = 0.5*(r1_km+r2_km); v1=np.sqrt(mu/r1_km); v2=np.sqrt(mu/r2_km)
    vp=np.sqrt(mu*(2/r1_km-1/a_t)); va=np.sqrt(mu*(2/r2_km-1/a_t)); dv1=abs(vp-v1); dv2=abs(v2-va)
    return HohmannTransfer(r1_km,r2_km,float(dv1),float(dv2),float(dv1+dv2),float(np.pi*np.sqrt(a_t**3/mu)))

def plane_change_delta_v(v_km_s: float, angle_rad: float) -> float:
    """Magnitude of a pure impulsive plane change for constant speed."""
    _positive(v_km_s, "v_km_s")
    if not 0 <= angle_rad <= np.pi: raise ValueError("angle_rad must be in [0, pi]")
    return float(2*v_km_s*np.sin(angle_rad/2))

@dataclass(frozen=True)
class BiEllipticTransfer:
    r1_km: float; rb_km: float; r2_km: float; delta_v1_km_s: float; delta_v2_km_s: float; delta_v3_km_s: float; total_delta_v_km_s: float; transfer_time_s: float

def bielliptic_transfer(r1_km: float, rb_km: float, r2_km: float, mu: float = MU_EARTH_KM3_S2) -> BiEllipticTransfer:
    for value,name in [(r1_km,"r1_km"),(rb_km,"rb_km"),(r2_km,"r2_km")]: _positive(value,name)
    if rb_km <= max(r1_km,r2_km): raise ValueError("rb_km must exceed both endpoint radii")
    a1=0.5*(r1_km+rb_km); a2=0.5*(r2_km+rb_km)
    v1=np.sqrt(mu/r1_km); vb1=np.sqrt(mu*(2/r1_km-1/a1)); vb2=np.sqrt(mu*(2/r2_km-1/a2)); v2=np.sqrt(mu/r2_km)
    dv1=abs(vb1-v1); dv2=abs(vb2-vb1); dv3=abs(v2-vb2); t=np.pi*np.sqrt(a1**3/mu)+np.pi*np.sqrt(a2**3/mu)
    return BiEllipticTransfer(r1_km,rb_km,r2_km,float(dv1),float(dv2),float(dv3),float(dv1+dv2+dv3),float(t))
