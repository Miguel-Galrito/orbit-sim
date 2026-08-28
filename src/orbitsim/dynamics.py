"""Acceleration models for orbital propagation."""
from __future__ import annotations
import numpy as np
from .constants import J2_EARTH, MU_EARTH_KM3_S2, OMEGA_EARTH_RAD_S, R_EARTH_KM

def two_body_acceleration(r_km: np.ndarray, mu: float = MU_EARTH_KM3_S2) -> np.ndarray:
    r=np.asarray(r_km,float); n=np.linalg.norm(r)
    if n==0: raise ValueError("position norm cannot be zero")
    return -mu*r/n**3

def j2_acceleration(r_km: np.ndarray, mu: float = MU_EARTH_KM3_S2, radius_km: float = R_EARTH_KM, j2: float = J2_EARTH) -> np.ndarray:
    x,y,z=np.asarray(r_km,float); r2=x*x+y*y+z*z; r=np.sqrt(r2)
    if r==0: raise ValueError("position norm cannot be zero")
    factor=1.5*j2*mu*radius_km**2/r**5; q=5*z*z/r2
    return factor*np.array([x*(q-1),y*(q-1),z*(q-3)])

def drag_acceleration(r_km: np.ndarray, v_km_s: np.ndarray, density_kg_m3: float, ballistic_coeff_m2_kg: float, omega_earth_rad_s: float = OMEGA_EARTH_RAD_S) -> np.ndarray:
    r=np.asarray(r_km,float); v=np.asarray(v_km_s,float)
    if density_kg_m3<0 or ballistic_coeff_m2_kg<0: raise ValueError("density and ballistic coefficient must be non-negative")
    vatm=np.cross([0.,0.,omega_earth_rad_s],r); vrel=(v-vatm)*1000; speed=np.linalg.norm(vrel)
    return np.zeros(3) if speed==0 else -0.5*density_kg_m3*ballistic_coeff_m2_kg*speed*vrel/1000
