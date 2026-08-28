"""Post-processing and simple analysis helpers."""
from __future__ import annotations
import numpy as np
from .constants import R_EARTH_KM,OMEGA_EARTH_RAD_S

def specific_energy(r_km,v_km_s,mu=398600.4418):return float(np.dot(v_km_s,v_km_s)/2-mu/np.linalg.norm(r_km))
def orbital_period_from_a(a_km,mu=398600.4418):
    if a_km<=0:raise ValueError("a_km must be positive")
    return float(2*np.pi*np.sqrt(a_km**3/mu))
def ground_track(times_s,positions_eci_km,earth_rotation_rad_s=OMEGA_EARTH_RAD_S):
    r=np.asarray(positions_eci_km);t=np.asarray(times_s);lon_eci=np.arctan2(r[:,1],r[:,0]);lon=(lon_eci-earth_rotation_rad_s*t+np.pi)%(2*np.pi)-np.pi;lat=np.arcsin(np.clip(r[:,2]/np.linalg.norm(r,axis=1),-1,1));return np.degrees(lon),np.degrees(lat)
def altitude_km(positions_km,radius_km=R_EARTH_KM):return np.linalg.norm(positions_km,axis=1)-radius_km
