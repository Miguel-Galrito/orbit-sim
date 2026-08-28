import numpy as np
from orbitsim import OrbitalElements,elements_to_state,state_to_elements,propagate
from orbitsim.constants import MU_EARTH_KM3_S2,R_EARTH_KM

def test_elements_round_trip():
 e=OrbitalElements(R_EARTH_KM+500,.02,np.deg2rad(35),np.deg2rad(40),np.deg2rad(20),np.deg2rad(70));out=state_to_elements(elements_to_state(e));assert np.isclose(out.a_km,e.a_km,rtol=1e-10);assert np.isclose(out.e,e.e,rtol=1e-10);assert np.isclose(out.i_rad,e.i_rad,rtol=1e-10)
def test_two_body_energy_is_nearly_conserved():
 r=R_EARTH_KM+400;state=elements_to_state(OrbitalElements(r,.001,0,0,0,0));res=propagate(state,5400,20);energy=np.sum(res.velocities_km_s**2,axis=1)/2-MU_EARTH_KM3_S2/np.linalg.norm(res.positions_km,axis=1);assert abs(energy[-1]-energy[0])<1e-7
def test_rk4_stays_finite():
 state=elements_to_state(OrbitalElements(R_EARTH_KM+700,.1,np.deg2rad(98),.1,.2,.3));res=propagate(state,7200,30);assert np.isfinite(res.states).all()
