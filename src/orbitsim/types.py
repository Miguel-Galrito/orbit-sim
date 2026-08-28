"""Data models used by the orbital mechanics engine."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class StateVector:
    """Cartesian inertial state, position in km and velocity in km/s."""
    r: np.ndarray
    v: np.ndarray
    def __post_init__(self) -> None:
        r = np.asarray(self.r, dtype=float); v = np.asarray(self.v, dtype=float)
        if r.shape != (3,) or v.shape != (3,): raise ValueError("r and v must each have shape (3,)")
        object.__setattr__(self, "r", r); object.__setattr__(self, "v", v)
    def as_array(self) -> np.ndarray: return np.concatenate((self.r, self.v))

@dataclass(frozen=True)
class OrbitalElements:
    a_km: float; e: float; i_rad: float; raan_rad: float; arg_perigee_rad: float; true_anomaly_rad: float

@dataclass(frozen=True)
class Maneuver:
    epoch_s: float; delta_v_km_s: np.ndarray; frame: str = "inertial"
    def __post_init__(self) -> None:
        dv = np.asarray(self.delta_v_km_s, dtype=float)
        if dv.shape != (3,): raise ValueError("delta_v_km_s must have shape (3,)")
        object.__setattr__(self, "delta_v_km_s", dv)
