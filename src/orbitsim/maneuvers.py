"""Classical impulsive maneuver utilities."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from .constants import MU_EARTH_KM3_S2
@dataclass(frozen=True)
class HohmannTransfer:
    r1_km:float;r2_km:float;delta_v1_km_s:float;delta_v2_km_s:float;total_delta_v_km_s:float;transfer_time_s:float

def hohmann_transfer(r1_km,r2_km,mu=MU_EARTH_KM3_S2):
    if r1_km<=0 or r2_km<=0 or np.isclose(r1_km,r2_km):raise ValueError("radii must be positive and distinct")
    at=.5*(r1_km+r2_km); v1=np.sqrt(mu/r1_km);v2=np.sqrt(mu/r2_km);vp=np.sqrt(mu*(2/r1_km-1/at));va=np.sqrt(mu*(2/r2_km-1/at));dv1=abs(vp-v1);dv2=abs(v2-va);t=np.pi*np.sqrt(at**3/mu)
    return HohmannTransfer(r1_km,r2_km,float(dv1),float(dv2),float(dv1+dv2),float(t))
