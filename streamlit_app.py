from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from orbitsim import OrbitalElements, elements_to_state, propagate, sun_earth_moon_demo
from orbitsim.analysis import altitude_km, ground_track, orbital_period_from_a, specific_energy
from orbitsim.constants import MU_EARTH_KM3_S2, R_EARTH_KM
from orbitsim.maneuvers import hohmann_transfer, plane_change_delta_v

st.set_page_config(page_title="Orbit Sim | Astrodynamics Lab", page_icon="🛰️", layout="wide")

st.markdown("""
<style>
.stApp{background:linear-gradient(180deg,#06111f 0%,#081626 100%)}
[data-testid="stSidebar"]{background:#0a1626;border-right:1px solid #17304d}
.hero{padding:8px 0 18px}.eyebrow{color:#67e8f9;font-size:.78rem;letter-spacing:.18em;text-transform:uppercase;font-weight:800}
.hero h1{font-size:3.2rem;line-height:1;margin:.2rem 0 .5rem}.hero p{color:#9fb2c8;font-size:1.04rem;max-width:920px}
.badge{display:inline-block;padding:7px 12px;border-radius:999px;background:#0e2945;border:1px solid #1d496f;color:#d8ebff;font-size:.82rem}
div[data-testid="stMetric"]{background:#0b1b2d;border:1px solid #183b5c;padding:14px;border-radius:16px}
</style>
""", unsafe_allow_html=True)


def earth_surface(radius: float = R_EARTH_KM):
    u=np.linspace(0,2*np.pi,72); v=np.linspace(0,np.pi,36)
    return radius*np.outer(np.cos(u),np.sin(v)), radius*np.outer(np.sin(u),np.sin(v)), radius*np.outer(np.ones_like(u),np.cos(v))


def orbit_player(positions: np.ndarray, times_s: np.ndarray, title: str) -> go.Figure:
    ex,ey,ez=earth_surface()
    fig=go.Figure()
    fig.add_surface(x=ex,y=ey,z=ez,opacity=.76,colorscale=[[0,"#0d2741"],[.5,"#1e5b8f"],[1,"#3c8bc7"]],showscale=False,hoverinfo="skip")
    fig.add_trace(go.Scatter3d(x=positions[:,0],y=positions[:,1],z=positions[:,2],mode="lines",name="Trajectory",line=dict(color="#67e8f9",width=5)))
    fig.add_trace(go.Scatter3d(x=[positions[0,0]],y=[positions[0,1]],z=[positions[0,2]],mode="markers",name="Start",marker=dict(size=7,color="#a78bfa")))
    fig.add_trace(go.Scatter3d(x=[positions[0,0]],y=[positions[0,1]],z=[positions[0,2]],mode="markers",name="Spacecraft",marker=dict(size=9,color="#fbbf24")))
    frame_idx=np.linspace(0,len(positions)-1,min(90,len(positions)),dtype=int)
    fig.frames=[go.Frame(name=str(i),data=[go.Scatter3d(x=[positions[i,0]],y=[positions[i,1]],z=[positions[i,2]],mode="markers",marker=dict(size=9,color="#fbbf24"))],traces=[3]) for i in frame_idx]
    fig.update_layout(
        title=title,margin=dict(l=0,r=0,t=46,b=0),paper_bgcolor="#0b1b2d",font=dict(color="#dbeafe"),
        legend=dict(orientation="h",y=1.02,x=0),scene=dict(bgcolor="#06111f",aspectmode="data",xaxis=dict(title="X (km)",gridcolor="#17324e"),yaxis=dict(title="Y (km)",gridcolor="#17324e"),zaxis=dict(title="Z (km)",gridcolor="#17324e")),
        updatemenus=[dict(type="buttons",direction="left",x=.02,y=.02,buttons=[
            dict(label="▶ Play",method="animate",args=[None,{"frame":{"duration":65,"redraw":True},"transition":{"duration":0},"fromcurrent":True}]),
            dict(label="⏸ Pause",method="animate",args=[[None],{"mode":"immediate","frame":{"duration":0,"redraw":False},"transition":{"duration":0}}])
        ])],
        sliders=[dict(active=0,x=.18,y=.02,len=.78,currentvalue={"prefix":"Time: "},steps=[dict(label=f"{times_s[i]/60:.1f} min",method="animate",args=[[str(i)],{"mode":"immediate","frame":{"duration":0,"redraw":True},"transition":{"duration":0}}]) for i in frame_idx])]
    )
    return fig


def line_chart(x,y,title,x_title,y_title):
    fig=go.Figure(go.Scatter(x=x,y=y,mode="lines",line=dict(color="#67e8f9",width=2.6)))
    fig.update_layout(title=title,margin=dict(l=0,r=0,t=42,b=0),paper_bgcolor="#0b1b2d",plot_bgcolor="#071524",font=dict(color="#dbeafe"),xaxis=dict(title=x_title,gridcolor="#17324e"),yaxis=dict(title=y_title,gridcolor="#17324e"))
    return fig


def nbody_figure(result):
    fig=go.Figure(); labels=["Sun","Earth","Moon"]; sizes=[13,8,6]
    for i,(label,size) in enumerate(zip(labels,sizes)):
        p=result.positions_km[:,i,:]
        fig.add_trace(go.Scatter3d(x=p[:,0],y=p[:,1],z=p[:,2],mode="lines",name=label,line=dict(width=4)))
        fig.add_trace(go.Scatter3d(x=[p[-1,0]],y=[p[-1,1]],z=[p[-1,2]],mode="markers",name=f"{label} now",marker=dict(size=size)))
    fig.update_layout(title="Sun–Earth–Moon N-body experiment",margin=dict(l=0,r=0,t=46,b=0),paper_bgcolor="#0b1b2d",font=dict(color="#dbeafe"),scene=dict(bgcolor="#06111f",aspectmode="data",xaxis_title="X (km)",yaxis_title="Y (km)",zaxis_title="Z (km)"))
    return fig


st.markdown('<div class="hero"><div class="eyebrow">Astrodynamics laboratory</div><h1>🛰️ Orbit Sim</h1><p>Propagate spacecraft, watch them move through time, analyse the physics, design transfers, and experiment with multi-body gravity.</p></div>',unsafe_allow_html=True)

st.sidebar.markdown("### Scenario")
presets={"Custom LEO":(400.,51.6,.001),"ISS-like LEO":(420.,51.64,.0005),"Polar orbit":(600.,90.,.001),"Highly elliptical":(500.,63.4,.15),"GEO":(35786.,0.,.001)}
scenario=st.sidebar.selectbox("Preset",list(presets)); d_alt,d_inc,d_e=presets[scenario]
altitude=st.sidebar.slider("Perigee altitude (km)",180.,35786.,d_alt,10.)
inclination=st.sidebar.slider("Inclination (deg)",0.,180.,d_inc,.1)
eccentricity=st.sidebar.slider("Eccentricity",0.,.80,d_e,.001)
orbits=st.sidebar.slider("Simulation length (orbits)",.25,12.,2.,.25)
model=st.sidebar.selectbox("Force model",["two-body","j2","drag"])
dt=st.sidebar.slider("Integrator step (s)",2,60,10)
st.sidebar.caption("Initial true anomaly ν = 0° (periapsis).")

perigee_radius=R_EARTH_KM+altitude
a=perigee_radius/(1-eccentricity) if eccentricity<1 else np.inf
apoapsis_altitude=a*(1+eccentricity)-R_EARTH_KM
if apoapsis_altitude<=0:
    st.error("Invalid orbit: apogee lies inside Earth. Increase altitude or reduce eccentricity."); st.stop()
period=orbital_period_from_a(a)
state0=elements_to_state(OrbitalElements(a,eccentricity,np.deg2rad(inclination),0.,0.,0.))
with st.spinner("Propagating trajectory…"):
    result=propagate(state0,orbits*period,dt,model=model,density_kg_m3=4e-12,ballistic_coeff_m2_kg=.01)
alts=altitude_km(result.positions_km)

cols=st.columns(5)
cols[0].metric("Semi-major axis",f"{a:,.1f} km"); cols[1].metric("Period",f"{period/60:.1f} min"); cols[2].metric("Perigee",f"{altitude:,.0f} km"); cols[3].metric("Apogee",f"{apoapsis_altitude:,.0f} km"); cols[4].metric("Samples",f"{len(result.times_s):,}")
st.markdown(f'<span class="badge">Model: {model} · RK4 · ECI · time-aware simulator</span>',unsafe_allow_html=True)
if np.any(alts<0): st.warning("The propagated trajectory intersects Earth. This model is not a re-entry solver.")

t1,t2,t3,t4=st.tabs(["🚀 Orbit player","📈 Analysis","🎯 Mission design","🌞 N-body lab"])
with t1:
    st.plotly_chart(orbit_player(result.positions_km,result.times_s,"3D Earth-centered trajectory"),use_container_width=True,config={"displaylogo":False})
    st.info("Press **▶ Play** inside the chart to watch the spacecraft move. The slider jumps through simulated time.")
    c1,c2=st.columns(2); lon,lat=ground_track(result.times_s,result.positions_km)
    gt=go.Figure(go.Scatter(x=lon,y=lat,mode="lines",line=dict(color="#a78bfa",width=2.5))); gt.update_layout(title="Ground track",margin=dict(l=0,r=0,t=42,b=0),paper_bgcolor="#0b1b2d",plot_bgcolor="#071524",font=dict(color="#dbeafe"),xaxis=dict(title="Longitude (deg)",range=[-180,180],gridcolor="#17324e"),yaxis=dict(title="Latitude (deg)",range=[-90,90],gridcolor="#17324e")); c1.plotly_chart(gt,use_container_width=True,config={"displaylogo":False})
    c2.plotly_chart(line_chart(result.times_s/60,alts,"Altitude vs time","Time (min)","Altitude (km)"),use_container_width=True,config={"displaylogo":False})
with t2:
    c1,c2=st.columns(2); energies=np.array([specific_energy(s[:3],s[3:]) for s in result.states]); speeds=np.linalg.norm(result.velocities_km_s,axis=1)
    c1.plotly_chart(line_chart(result.times_s/60,energies,"Specific orbital energy","Time (min)","km²/s²"),use_container_width=True,config={"displaylogo":False}); c2.plotly_chart(line_chart(result.times_s/60,speeds,"Orbital speed","Time (min)","km/s"),use_container_width=True,config={"displaylogo":False})
    table=pd.DataFrame({"Parameter":["Force model","Inclination","Eccentricity","Perigee altitude","Apogee altitude","Minimum altitude","Maximum altitude"],"Value":[model,f"{inclination:.2f}°",f"{eccentricity:.4f}",f"{altitude:.1f} km",f"{apoapsis_altitude:.1f} km",f"{np.min(alts):.1f} km",f"{np.max(alts):.1f} km"]}); st.dataframe(table,use_container_width=True,hide_index=True)
with t3:
    st.subheader("Hohmann transfer"); c1,c2,c3=st.columns(3); r1=c1.number_input("Initial circular altitude (km)",min_value=180.,value=400.,step=50.); r2=c2.number_input("Final circular altitude (km)",min_value=180.,value=35786.,step=50.); h=hohmann_transfer(R_EARTH_KM+r1,R_EARTH_KM+r2); c3.metric("Total Δv",f"{h.total_delta_v_km_s:.3f} km/s"); st.write({"Burn 1":f"{h.delta_v1_km_s:.3f} km/s","Burn 2":f"{h.delta_v2_km_s:.3f} km/s","Transfer time":f"{h.transfer_time_s/3600:.2f} h"})
    st.subheader("Plane change"); c1,c2,c3=st.columns(3); speed=c1.number_input("Velocity (km/s)",min_value=.1,value=7.7,step=.1); angle=c2.number_input("Plane change (deg)",min_value=0.,max_value=180.,value=10.,step=1.); c3.metric("Δv",f"{plane_change_delta_v(speed,np.deg2rad(angle)):.3f} km/s")
    df=pd.DataFrame(result.states,columns=["x_km","y_km","z_km","vx_km_s","vy_km_s","vz_km_s"]); df.insert(0,"time_s",result.times_s); st.download_button("Download trajectory CSV",df.to_csv(index=False).encode(),"orbit_trajectory.csv","text/csv")
with t4:
    st.write("A separate point-mass experiment. Every body attracts every other body; this is intentionally simple so the numerical method remains inspectable.")
    days=st.slider("Duration (days)",7,120,30,1); hours=st.slider("Time step (hours)",1,12,6,1)
    with st.spinner("Integrating Sun–Earth–Moon…"): nb=sun_earth_moon_demo(float(days),float(hours))
    st.plotly_chart(nbody_figure(nb),use_container_width=True,config={"displaylogo":False})
    st.caption(f"{len(nb.times_s):,} samples · {days} days · {hours} h step · classical RK4")
    st.warning("This N-body mode is an educational experiment, not a precision ephemeris or flight-dynamics model.")

st.divider(); st.caption("Orbit Sim — educational/research software. Simplified models are for learning and prototyping.")
