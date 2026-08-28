"""Conversions between Cartesian state vectors and classical orbital elements."""
from __future__ import annotations
import numpy as np
from .constants import MU_EARTH_KM3_S2
from .types import OrbitalElements, StateVector
_EPS = 1e-12

def elements_to_state(elements: OrbitalElements, mu: float = MU_EARTH_KM3_S2) -> StateVector:
    a,e,inc,raan,argp,nu = elements.a_km,elements.e,elements.i_rad,elements.raan_rad,elements.arg_perigee_rad,elements.true_anomaly_rad
    if a <= 0 or not (0 <= e < 1): raise ValueError("positive a and 0 <= e < 1 required")
    p=a*(1-e*e); den=1+e*np.cos(nu)
    r_pf=np.array([p*np.cos(nu)/den,p*np.sin(nu)/den,0.0]); v_pf=np.sqrt(mu/p)*np.array([-np.sin(nu),e+np.cos(nu),0.0])
    cO,sO,co,so,ci,si=np.cos(raan),np.sin(raan),np.cos(argp),np.sin(argp),np.cos(inc),np.sin(inc)
    R=np.array([[cO*co-sO*so*ci,-cO*so-sO*co*ci,sO*si],[sO*co+cO*so*ci,-sO*so+cO*co*ci,-cO*si],[so*si,co*si,ci]])
    return StateVector(R@r_pf,R@v_pf)

def state_to_elements(state: StateVector, mu: float = MU_EARTH_KM3_S2) -> OrbitalElements:
    r,v=state.r,state.v; rm,vm=np.linalg.norm(r),np.linalg.norm(v); h=np.cross(r,v); hm=np.linalg.norm(h)
    if rm<_EPS or hm<_EPS: raise ValueError("degenerate state")
    i=np.arccos(np.clip(h[2]/hm,-1,1)); n=np.cross([0.,0.,1.],h); nm=np.linalg.norm(n)
    evec=np.cross(v,h)/mu-r/rm; e=np.linalg.norm(evec); energy=vm**2/2-mu/rm
    if abs(energy)<_EPS: raise ValueError("parabolic orbit not supported")
    a=-mu/(2*energy); raan=np.arctan2(n[1],n[0])%(2*np.pi) if nm>_EPS else 0.0
    if e>_EPS and nm>_EPS:
        argp=np.arccos(np.clip(np.dot(n,evec)/(nm*e),-1,1)); argp=2*np.pi-argp if evec[2]<0 else argp
    else: argp=0.0
    if e>_EPS:
        nu=np.arccos(np.clip(np.dot(evec,r)/(e*rm),-1,1)); nu=2*np.pi-nu if np.dot(r,v)<0 else nu
    else:
        cp=np.dot(n,r)/(nm*rm) if nm>_EPS else r[0]/rm; nu=np.arccos(np.clip(cp,-1,1)); nu=2*np.pi-nu if r[2]<0 else nu
    return OrbitalElements(float(a),float(e),float(i),float(raan),float(argp),float(nu))
