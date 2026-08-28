"""Numerical propagation using fixed-step RK4."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable
import numpy as np
from .constants import MU_EARTH_KM3_S2
from .dynamics import drag_acceleration,j2_acceleration,two_body_acceleration
from .types import Maneuver,StateVector
AccelerationModel=Callable[[np.ndarray,np.ndarray],np.ndarray]
@dataclass(frozen=True)
class PropagationResult:
    times_s: np.ndarray
    states: np.ndarray
    @property
    def positions_km(self)->np.ndarray:return self.states[:,:3]
    @property
    def velocities_km_s(self)->np.ndarray:return self.states[:,3:]

def _rhs(y,acceleration):return np.concatenate((y[3:],acceleration(y[:3],y[3:])))

def propagate(state0,duration_s,dt_s=10.0,model="two-body",density_kg_m3=0.0,ballistic_coeff_m2_kg=0.0,mu=MU_EARTH_KM3_S2):
    if duration_s<=0 or dt_s<=0:raise ValueError("duration_s and dt_s must be positive")
    if model not in {"two-body","j2","drag"}:raise ValueError("model must be two-body, j2, or drag")
    def acc(r,v):
        a=two_body_acceleration(r,mu)
        if model=="j2":a+=j2_acceleration(r,mu)
        elif model=="drag":a+=drag_acceleration(r,v,density_kg_m3,ballistic_coeff_m2_kg)
        return a
    n=int(np.ceil(duration_s/dt_s)); times=np.linspace(0,duration_s,n+1); dt=duration_s/n; states=np.empty((n+1,6)); states[0]=state0.as_array()
    for k in range(n):
        y=states[k]; k1=_rhs(y,acc); k2=_rhs(y+.5*dt*k1,acc); k3=_rhs(y+.5*dt*k2,acc); k4=_rhs(y+dt*k3,acc); states[k+1]=y+dt*(k1+2*k2+2*k3+k4)/6
    return PropagationResult(times,states)

def propagate_with_maneuvers(state0,duration_s,dt_s,maneuvers,model="two-body"):
    maneuvers=sorted(maneuvers,key=lambda m:m.epoch_s); current=state0; epoch=0.; all_times=[]; all_states=[]
    for m in maneuvers+[Maneuver(duration_s,np.zeros(3))]:
        if m.epoch_s<epoch or m.epoch_s>duration_s:raise ValueError("maneuver epochs must be ordered within interval")
        span=m.epoch_s-epoch
        if span>0:
            res=propagate(current,span,dt_s,model=model); shifted=res.times_s+epoch
            if all_states:
                all_times.extend(shifted[1:].tolist()); all_states.append(res.states[1:])
            else:
                all_times.extend(shifted.tolist()); all_states.append(res.states)
            current=StateVector(res.states[-1,:3],res.states[-1,3:]); epoch=m.epoch_s
        if m.epoch_s<duration_s:
            if m.frame!="inertial":raise NotImplementedError("only inertial burns are supported")
            current=StateVector(current.r,current.v+m.delta_v_km_s)
    return PropagationResult(np.asarray(all_times),np.vstack(all_states))
