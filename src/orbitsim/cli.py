"""Command-line entry point for Orbit Sim."""
from __future__ import annotations
import argparse,csv
import numpy as np
from .constants import MU_EARTH_KM3_S2,R_EARTH_KM
from .elements import elements_to_state
from .propagation import propagate
from .types import OrbitalElements

def main():
 p=argparse.ArgumentParser(description="Propagate a near-circular Earth orbit");p.add_argument("--altitude-km",type=float,default=400);p.add_argument("--inclination-deg",type=float,default=51.6);p.add_argument("--duration-orbits",type=float,default=1);p.add_argument("--dt-s",type=float,default=10);p.add_argument("--model",choices=["two-body","j2","drag"],default="two-body");p.add_argument("--output",default="trajectory.csv");a=p.parse_args()
 r=R_EARTH_KM+a.altitude_km;period=2*np.pi*np.sqrt(r**3/MU_EARTH_KM3_S2);state=elements_to_state(OrbitalElements(r,.001,np.deg2rad(a.inclination_deg),0,0,0));res=propagate(state,a.duration_orbits*period,a.dt_s,a.model,density_kg_m3=4e-12,ballistic_coeff_m2_kg=.01)
 with open(a.output,"w",newline="",encoding="utf-8") as f:
  w=csv.writer(f);w.writerow(["time_s","x_km","y_km","z_km","vx_km_s","vy_km_s","vz_km_s"]);w.writerows(np.column_stack((res.times_s,res.states)))
 print(f"Wrote {len(res.times_s)} samples to {a.output}")
