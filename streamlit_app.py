from __future__ import annotations

import io

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from orbitsim import OrbitalElements, elements_to_state, propagate
from orbitsim.analysis import altitude_km, ground_track, orbital_period_from_a, specific_energy
from orbitsim.constants import MU_EARTH_KM3_S2, R_EARTH_KM

st.set_page_config(
    page_title="Orbit Sim | Astrodynamics Lab",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- styling ----------
st.markdown(
    """
    <style>
    .stApp { background: #07111f; }
    [data-testid="stSidebar"] { background: #0b1728; }
    .hero { padding: 12px 0 24px 0; }
    .eyebrow { color:#67e8f9; font-size:0.78rem; letter-spacing:0.16em; text-transform:uppercase; font-weight:700; }
    .hero h1 { font-size:3rem; line-height:1.0; margin:0.2rem 0 0.6rem; }
    .hero p { color:#a9b8ca; font-size:1.02rem; margin:0; max-width:900px; }
    .status { padding:8px 12px; border-radius:999px; background:#10253d; color:#d8e7f8; display:inline-block; font-size:0.82rem; }
    div[data-testid="stMetric"] { background:#0d1a2b; border:1px solid #1d3551; padding:14px; border-radius:14px; }
    .card { background:#0d1a2b; border:1px solid #1d3551; border-radius:16px; padding:16px 18px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- helpers ----------
def earth_figure(positions_km: np.ndarray, title: str, show_inertial_axes: bool = True) -> go.Figure:
    u = np.linspace(0, 2 * np.pi, 80)
    v = np.linspace(0, np.pi, 40)
    x = R_EARTH_KM * np.outer(np.cos(u), np.sin(v))
    y = R_EARTH_KM * np.outer(np.sin(u), np.sin(v))
    z = R_EARTH_KM * np.outer(np.ones_like(u), np.cos(v))

    fig = go.Figure()
    fig.add_surface(x=x, y=y, z=z, opacity=0.72, colorscale=[[0, "#12365a"], [1, "#2b6cb0"]], showscale=False)
    fig.add_trace(
        go.Scatter3d(
            x=positions_km[:, 0], y=positions_km[:, 1], z=positions_km[:, 2],
            mode="lines", name="Spacecraft",
            line=dict(color="#67e8f9", width=5),
        )
    )
    fig.add_trace(
        go.Scatter3d(
            x=[positions_km[-1, 0]], y=[positions_km[-1, 1]], z=[positions_km[-1, 2]],
            mode="markers", name="Final state",
            marker=dict(size=7, color="#fbbf24"),
        )
    )
    if show_inertial_axes:
        lim = max(float(np.max(np.linalg.norm(positions_km, axis=1))), R_EARTH_KM) * 1.12
        for axis, end in [("X", (lim, 0, 0)), ("Y", (0, lim, 0)), ("Z", (0, 0, lim))]:
            fig.add_trace(go.Scatter3d(x=[0, end[0]], y=[0, end[1]], z=[0, end[2]], mode="lines+text", text=["", axis], name=f"ECI {axis}", line=dict(width=2, dash="dot")))
    fig.update_layout(
        title=title,
        margin=dict(l=0, r=0, t=45, b=0),
        paper_bgcolor="#0d1a2b",
        plot_bgcolor="#0d1a2b",
        font=dict(color="#dbeafe"),
        legend=dict(orientation="h", y=1.02, x=0),
        scene=dict(
            bgcolor="#07111f",
            xaxis=dict(title="X (km)", gridcolor="#233b55", zerolinecolor="#38546e"),
            yaxis=dict(title="Y (km)", gridcolor="#233b55", zerolinecolor="#38546e"),
            zaxis=dict(title="Z (km)", gridcolor="#233b55", zerolinecolor="#38546e"),
            aspectmode="data",
        ),
    )
    return fig


def line_chart(x, y, title, x_title, y_title):
    fig = go.Figure(go.Scatter(x=x, y=y, mode="lines", line=dict(color="#67e8f9", width=2.5)))
    fig.update_layout(
        title=title, margin=dict(l=0, r=0, t=45, b=0),
        paper_bgcolor="#0d1a2b", plot_bgcolor="#0d1a2b", font=dict(color="#dbeafe"),
        xaxis=dict(title=x_title, gridcolor="#233b55"), yaxis=dict(title=y_title, gridcolor="#233b55"),
    )
    return fig


# ---------- header ----------
st.markdown(
    '<div class="hero"><div class="eyebrow">Astrodynamics laboratory</div><h1>🛰️ Orbit Sim</h1><p>Interactive orbital mechanics: propagate, inspect, compare force models and experiment with mission-design parameters.</p></div>',
    unsafe_allow_html=True,
)

# ---------- sidebar ----------
st.sidebar.markdown("### Scenario")
scenario = st.sidebar.selectbox("Preset", ["Custom LEO", "ISS-like LEO", "Polar orbit", "Highly elliptical", "GEO"])

presets = {
    "Custom LEO": dict(altitude=400.0, inclination=51.6, eccentricity=0.001),
    "ISS-like LEO": dict(altitude=420.0, inclination=51.64, eccentricity=0.0005),
    "Polar orbit": dict(altitude=600.0, inclination=90.0, eccentricity=0.001),
    "Highly elliptical": dict(altitude=500.0, inclination=63.4, eccentricity=0.35),
    "GEO": dict(altitude=35786.0, inclination=0.0, eccentricity=0.001),
}
p = presets[scenario]

altitude = st.sidebar.slider("Perigee altitude (km)", 180.0, 35786.0, p["altitude"], 10.0)
inclination = st.sidebar.slider("Inclination (deg)", 0.0, 180.0, p["inclination"], 0.1)
eccentricity = st.sidebar.slider("Eccentricity", 0.0, 0.80, p["eccentricity"], 0.001)
orbits = st.sidebar.slider("Simulation length (orbits)", 0.25, 12.0, 2.0, 0.25)
model = st.sidebar.selectbox("Force model", ["two-body", "j2", "drag"])
dt = st.sidebar.slider("Integrator step (s)", 2, 60, 10)
st.sidebar.divider()
st.sidebar.caption("Start at true anomaly ν = 0° (periapsis).")

# Prevent hidden invalid scenarios.
perigee_radius = R_EARTH_KM + altitude
if eccentricity > 0.0:
    a = perigee_radius / (1.0 - eccentricity)
else:
    a = perigee_radius
apoapsis_altitude = a * (1.0 + eccentricity) - R_EARTH_KM

if perigee_radius <= R_EARTH_KM:
    st.error("The initial orbit intersects Earth. Increase altitude.")
    st.stop()
if apoapsis_altitude <= 0:
    st.error("This eccentricity/altitude combination produces an orbit intersecting Earth.")
    st.stop()

period = orbital_period_from_a(a)
state0 = elements_to_state(
    OrbitalElements(
        a_km=a,
        e=eccentricity,
        i_rad=np.deg2rad(inclination),
        raan_rad=0.0,
        arg_perigee_rad=0.0,
        true_anomaly_rad=0.0,
    )
)

with st.spinner("Propagating trajectory…"):
    result = propagate(
        state0,
        duration_s=orbits * period,
        dt_s=dt,
        model=model,
        density_kg_m3=4e-12,
        ballistic_coeff_m2_kg=0.01,
    )

alts = altitude_km(result.positions_km)
impact = bool(np.any(alts < 0))
if impact:
    st.warning("The propagated trajectory intersects Earth. The force model is not intended for atmospheric re-entry; reduce eccentricity or increase altitude.")

# ---------- top metrics ----------
cols = st.columns(5)
cols[0].metric("Semi-major axis", f"{a:,.1f} km")
cols[1].metric("Period", f"{period/60:.1f} min")
cols[2].metric("Perigee", f"{altitude:,.0f} km")
cols[3].metric("Apogee", f"{apoapsis_altitude:,.0f} km")
cols[4].metric("Samples", f"{len(result.times_s):,}")

st.markdown('<span class="status">Model: ' + model + ' · RK4 · Earth-centered inertial frame</span>', unsafe_allow_html=True)

# ---------- main visualization ----------
tab1, tab2, tab3 = st.tabs(["🚀 Trajectory", "📈 Analysis", "🧭 Mission design"])

with tab1:
    st.plotly_chart(earth_figure(result.positions_km, "3D Earth-centered trajectory"), use_container_width=True, config={"displaylogo": False})
    left, right = st.columns(2)
    with left:
        lon, lat = ground_track(result.times_s, result.positions_km)
        gt = go.Figure(go.Scatter(x=lon, y=lat, mode="lines", line=dict(color="#a78bfa", width=2.5)))
        gt.update_layout(
            title="Ground track", margin=dict(l=0, r=0, t=45, b=0),
            paper_bgcolor="#0d1a2b", plot_bgcolor="#07111f", font=dict(color="#dbeafe"),
            xaxis=dict(title="Longitude (deg)", range=[-180, 180], gridcolor="#233b55"),
            yaxis=dict(title="Latitude (deg)", range=[-90, 90], gridcolor="#233b55"),
        )
        st.plotly_chart(gt, use_container_width=True, config={"displaylogo": False})
    with right:
        st.plotly_chart(line_chart(result.times_s / 60, alts, "Altitude", "Time (min)", "Altitude (km)"), use_container_width=True, config={"displaylogo": False})

with tab2:
    c1, c2 = st.columns(2)
    with c1:
        energies = np.array([specific_energy(s[:3], s[3:]) for s in result.states])
        st.plotly_chart(line_chart(result.times_s / 60, energies, "Specific orbital energy", "Time (min)", "km²/s²"), use_container_width=True, config={"displaylogo": False})
    with c2:
        speeds = np.linalg.norm(result.velocities_km_s, axis=1)
        st.plotly_chart(line_chart(result.times_s / 60, speeds, "Orbital speed", "Time (min)", "km/s"), use_container_width=True, config={"displaylogo": False})

    table = pd.DataFrame(
        {
            "Parameter": ["Force model", "Integrator", "dt", "Inclination", "Eccentricity", "Perigee altitude", "Apogee altitude", "Min propagated altitude", "Max propagated altitude"],
            "Value": [model, "RK4", f"{dt} s", f"{inclination:.2f}°", f"{eccentricity:.4f}", f"{altitude:.1f} km", f"{apoapsis_altitude:.1f} km", f"{np.min(alts):.1f} km", f"{np.max(alts):.1f} km"],
        }
    )
    st.dataframe(table, use_container_width=True, hide_index=True)

with tab3:
    st.markdown("#### Hohmann transfer calculator")
    c1, c2, c3 = st.columns(3)
    r1 = c1.number_input("Initial circular altitude (km)", min_value=180.0, value=400.0, step=50.0)
    r2 = c2.number_input("Final circular altitude (km)", min_value=180.0, value=35786.0, step=50.0)
    from orbitsim.maneuvers import hohmann_transfer
    h = hohmann_transfer(R_EARTH_KM + r1, R_EARTH_KM + r2)
    c3.metric("Total Δv", f"{h.total_delta_v_km_s:.3f} km/s")
    st.write({
        "First burn": f"{h.delta_v1_km_s:.3f} km/s",
        "Second burn": f"{h.delta_v2_km_s:.3f} km/s",
        "Transfer time": f"{h.transfer_time_s/3600:.2f} h",
    })

    st.markdown("#### Export")
    df = pd.DataFrame(result.states, columns=["x_km", "y_km", "z_km", "vx_km_s", "vy_km_s", "vz_km_s"])
    df.insert(0, "time_s", result.times_s)
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download trajectory CSV", data=csv_bytes, file_name="orbit_trajectory.csv", mime="text/csv")

st.divider()
st.caption("Orbit Sim is an educational/research simulator. Simplified perturbation models are intended for learning and prototyping, not flight operations.")
