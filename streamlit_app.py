from __future__ import annotations
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from orbitsim import OrbitalElements,elements_to_state,propagate
from orbitsim.analysis import altitude_km,ground_track,orbital_period_from_a
from orbitsim.constants import R_EARTH_KM
st.set_page_config(page_title="Orbit Sim",layout="wide")
st.title("🛰️ Orbit Sim")
st.caption("Educational orbital mechanics sandbox")
with st.sidebar:
 altitude=st.slider("Altitude (km)",180,20000,400);inclination=st.slider("Inclination (deg)",0.,180.,51.6);eccentricity=st.slider("Eccentricity",0.,.8,.001,.001);orbits=st.slider("Orbits",.25,10.,2.,.25);model=st.selectbox("Force model",["two-body","j2","drag"]);dt=st.slider("Step (s)",2,60,10)
r=R_EARTH_KM+altitude;period=orbital_period_from_a(r);state0=elements_to_state(OrbitalElements(r,eccentricity,np.deg2rad(inclination),0,0,0));result=propagate(state0,orbits*period,dt,model=model,density_kg_m3=4e-12,ballistic_coeff_m2_kg=.01)
c1,c2,c3=st.columns(3);c1.metric("Period",f"{period/60:.1f} min");c2.metric("Samples",f"{len(result.times_s):,}");c3.metric("Final altitude",f"{altitude_km(result.positions_km)[-1]:.1f} km")
fig=plt.figure(figsize=(8,7));ax=fig.add_subplot(111,projection="3d");xyz=result.positions_km;ax.plot(xyz[:,0],xyz[:,1],xyz[:,2],linewidth=1.2);ax.set_xlabel("x (km)");ax.set_ylabel("y (km)");ax.set_zlabel("z (km)");ax.set_title("ECI trajectory");st.pyplot(fig)
lon,lat=ground_track(result.times_s,result.positions_km);st.subheader("Ground track");gt,gax=plt.subplots(figsize=(10,3.5));gax.plot(lon,lat);gax.set_xlabel("Longitude (deg)");gax.set_ylabel("Latitude (deg)");gax.grid(True,alpha=.25);st.pyplot(gt)
