from __future__ import annotations

import io

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from orbitsim import (
    OrbitalElements,
    elements_to_state,
    propagate,
    sun_earth_moon_demo,
)
from orbitsim.analysis import altitude_km, ground_track, orbital_period_from_a, specific_energy
from orbitsim.constants import R_EARTH_KM
from orbitsim.maneuvers import hohmann_transfer


st.set_page_config(
    page_title="Orbit Sim | Astrodynamics Lab",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# -----------------------------------------------------------------------------
# Styling
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    .stApp { background: #07111f; }
    [data-testid="stSidebar"] { background: #0b1728; }
    .hero { padding: 10px 0 18px; }
    .eyebrow { color:#67e8f9; font-size:.78rem; letter-spacing:.16em; text-transform:uppercase; font-weight:800; }
    .hero h1 { font-size:3.1rem; line-height:1; margin:.25rem 0 .55rem; }
    .hero p { color:#a9b8ca; font-size:1.03rem; max-width:960px; margin:0; }
    .status { padding:8px 13px; border-radius:999px; background:#10253d; color:#d8e7f8; display:inline-block; font-size:.82rem; }
    .info-card { background:#0d1a2b; border:1px solid #1d3551; border-radius:16px; padding:16px 18px; height:100%; }
    .info-card .label { color:#8ea3ba; font-size:.78rem; text-transform:uppercase; letter-spacing:.06em; }
    .info-card .value { color:#e7f2ff; font-size:1.55rem; font-weight:750; margin-top:3px; }
    .info-card .note { color:#8296ac; font-size:.76rem; margin-top:3px; }
    div[data-testid="stMetric"] { background:#0d1a2b; border:1px solid #1d3551; padding:14px; border-radius:14px; }
    </style>
    """,
    unsafe_allow_html=True,
)


def info_card(label: str, value: str, note: str) -> None:
    st.markdown(
        f'<div class="info-card"><div class="label">{label}</div>'
        f'<div class="value">{value}</div><div class="note">{note}</div></div>',
        unsafe_allow_html=True,
    )


def earth_surface() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    u = np.linspace(0, 2 * np.pi, 72)
    v = np.linspace(0, np.pi, 36)
    x = R_EARTH_KM * np.outer(np.cos(u), np.sin(v))
    y = R_EARTH_KM * np.outer(np.sin(u), np.sin(v))
    z = R_EARTH_KM * np.outer(np.ones_like(u), np.cos(v))
    return x, y, z


def orbit_player_figure(positions_km: np.ndarray, times_s: np.ndarray) -> go.Figure:
    """Animated Earth-centered trajectory with full-orbit context and a time slider."""
    x, y, z = earth_surface()
    n_frames = min(120, len(times_s))
    frame_indices = np.linspace(0, len(times_s) - 1, n_frames, dtype=int)

    fig = go.Figure()
    fig.add_surface(
        x=x, y=y, z=z, opacity=0.80,
        colorscale=[[0.0, "#12365a"], [1.0, "#2f7acb"]],
        showscale=False, name="Earth",
        hoverinfo="skip",
    )
    fig.add_trace(
        go.Scatter3d(
            x=positions_km[:, 0], y=positions_km[:, 1], z=positions_km[:, 2],
            mode="lines", name="Full trajectory",
            line=dict(color="#25496b", width=2),
            hovertemplate="Full trajectory<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter3d(
            x=positions_km[: frame_indices[0] + 1, 0],
            y=positions_km[: frame_indices[0] + 1, 1],
            z=positions_km[: frame_indices[0] + 1, 2],
            mode="lines", name="Elapsed path",
            line=dict(color="#67e8f9", width=6),
        )
    )
    fig.add_trace(
        go.Scatter3d(
            x=[positions_km[frame_indices[0], 0]],
            y=[positions_km[frame_indices[0], 1]],
            z=[positions_km[frame_indices[0], 2]],
            mode="markers+text", name="Spacecraft",
            text=["🛰️"], textposition="top center",
            marker=dict(size=8, color="#fbbf24"),
            hovertemplate="t = %{customdata:.1f} min<extra></extra>",
            customdata=[times_s[frame_indices[0]] / 60],
        )
    )

    frames = []
    slider_steps = []
    for idx in frame_indices:
        trail = positions_km[: idx + 1]
        frames.append(
            go.Frame(
                name=f"t{idx}",
                data=[
                    go.Scatter3d(x=trail[:, 0], y=trail[:, 1], z=trail[:, 2], mode="lines", line=dict(color="#67e8f9", width=6)),
                    go.Scatter3d(x=[positions_km[idx, 0]], y=[positions_km[idx, 1]], z=[positions_km[idx, 2]], mode="markers+text", text=["🛰️"], textposition="top center", marker=dict(size=8, color="#fbbf24"), hovertemplate="t = %{customdata:.1f} min<extra></extra>", customdata=[times_s[idx] / 60]),
                ],
                traces=[2, 3],
            )
        )
        slider_steps.append(
            dict(
                label=f"{times_s[idx] / 60:.0f} min",
                method="animate",
                args=[[f"t{idx}"], {"mode": "immediate", "frame": {"duration": 0, "redraw": True}, "transition": {"duration": 0}}],
            )
        )

    fig.frames = frames
    total_min = times_s[-1] / 60
    fig.update_layout(
        title=f"3D Earth-centered trajectory · {total_min:.1f} min simulated",
        margin=dict(l=0, r=0, t=48, b=0),
        paper_bgcolor="#0d1a2b", plot_bgcolor="#0d1a2b", font=dict(color="#dbeafe"),
        legend=dict(orientation="h", y=1.02, x=0),
        scene=dict(
            bgcolor="#07111f",
            xaxis=dict(title="X (km)", gridcolor="#233b55", zerolinecolor="#38546e"),
            yaxis=dict(title="Y (km)", gridcolor="#233b55", zerolinecolor="#38546e"),
            zaxis=dict(title="Z (km)", gridcolor="#233b55", zerolinecolor="#38546e"),
            aspectmode="data",
        ),
        updatemenus=[
            dict(
                type="buttons", showactive=False, x=0.02, y=1.08,
                buttons=[
                    dict(
                        label="▶ Play",
                        method="animate",
                        args=[None, {"fromcurrent": True, "frame": {"duration": 80, "redraw": True}, "transition": {"duration": 0}}],
                    ),
                    dict(
                        label="⏸ Pause",
                        method="animate",
                        args=[[None], {"mode": "immediate", "frame": {"duration": 0, "redraw": False}, "transition": {"duration": 0}}],
                    ),
                ],
            )
        ],
        sliders=[
            dict(
                active=0,
                x=0.16, y=1.06, len=0.80,
                currentvalue={"prefix": "Simulation time: ", "suffix": " min"},
                steps=slider_steps,
            )
        ],
    )
    return fig


def line_chart(x: np.ndarray, y: np.ndarray, title: str, x_title: str, y_title: str) -> go.Figure:
    fig = go.Figure(go.Scatter(x=x, y=y, mode="lines", line=dict(color="#67e8f9", width=2.5)))
    fig.update_layout(
        title=title, margin=dict(l=0, r=0, t=45, b=0),
        paper_bgcolor="#0d1a2b", plot_bgcolor="#07111f", font=dict(color="#dbeafe"),
        xaxis=dict(title=x_title, gridcolor="#233b55"), yaxis=dict(title=y_title, gridcolor="#233b55"),
    )
    return fig


def nbody_solar_figure(result, play_speed: int = 120) -> go.Figure:
    """Solar-system-scale N-body view. Distances are shown in AU."""
    au = 149_597_870.7
    names = ["Sun", "Earth", "Moon"]
    symbols = ["☀️", "🌍", "🌙"]
    sizes = [17, 10, 7]
    scales = result.positions_km / au
    n_frames = min(100, len(result.times_s))
    frame_indices = np.linspace(0, len(result.times_s) - 1, n_frames, dtype=int)

    fig = go.Figure()
    for i, name in enumerate(names):
        fig.add_trace(go.Scatter3d(x=scales[:, i, 0], y=scales[:, i, 1], z=scales[:, i, 2], mode="lines", name=f"{symbols[i]} {name} path", line=dict(width=3)))
    for i, name in enumerate(names):
        idx = frame_indices[0]
        fig.add_trace(go.Scatter3d(x=[scales[idx, i, 0]], y=[scales[idx, i, 1]], z=[scales[idx, i, 2]], mode="markers+text", text=[symbols[i]], textposition="top center", name=name, marker=dict(size=sizes[i])))

    frames = []
    steps = []
    for idx in frame_indices:
        frames.append(
            go.Frame(
                name=f"nb{idx}",
                data=[
                    go.Scatter3d(x=[scales[idx, 0, 0]], y=[scales[idx, 0, 1]], z=[scales[idx, 0, 2]], mode="markers+text", text=["☀️"], textposition="top center", marker=dict(size=17)),
                    go.Scatter3d(x=[scales[idx, 1, 0]], y=[scales[idx, 1, 1]], z=[scales[idx, 1, 2]], mode="markers+text", text=["🌍"], textposition="top center", marker=dict(size=10)),
                    go.Scatter3d(x=[scales[idx, 2, 0]], y=[scales[idx, 2, 1]], z=[scales[idx, 2, 2]], mode="markers+text", text=["🌙"], textposition="top center", marker=dict(size=7)),
                ],
                traces=[3, 4, 5],
            )
        )
        steps.append(dict(label=f"{result.times_s[idx] / 86400:.0f} d", method="animate", args=[[f"nb{idx}"], {"mode": "immediate", "frame": {"duration": 0, "redraw": True}, "transition": {"duration": 0}}]))
    fig.frames = frames
    fig.update_layout(
        title="Solar-system view · distances in AU",
        margin=dict(l=0, r=0, t=48, b=0), paper_bgcolor="#0d1a2b", plot_bgcolor="#0d1a2b", font=dict(color="#dbeafe"),
        legend=dict(orientation="h", y=1.02, x=0),
        scene=dict(bgcolor="#07111f", aspectmode="data", xaxis=dict(title="X (AU)", gridcolor="#233b55"), yaxis=dict(title="Y (AU)", gridcolor="#233b55"), zaxis=dict(title="Z (AU)", gridcolor="#233b55")),
        updatemenus=[dict(type="buttons", showactive=False, x=.02, y=1.08, buttons=[dict(label="▶ Play", method="animate", args=[None, {"fromcurrent": True, "frame": {"duration": play_speed, "redraw": True}, "transition": {"duration": 0}}]), dict(label="⏸ Pause", method="animate", args=[[None], {"mode": "immediate", "frame": {"duration": 0}}])])],
        sliders=[dict(active=0, x=.16, y=1.06, len=.80, currentvalue={"prefix": "Time: ", "suffix": " days"}, steps=steps)],
    )
    return fig


def nbody_local_figure(result) -> go.Figure:
    """Earth-centered Moon view. Distances are shown in 1,000 km."""
    rel = (result.positions_km[:, 2, :] - result.positions_km[:, 1, :]) / 1000.0
    n_frames = min(120, len(result.times_s))
    frame_indices = np.linspace(0, len(result.times_s) - 1, n_frames, dtype=int)
    fig = go.Figure()
    fig.add_trace(go.Scatter3d(x=rel[:, 0], y=rel[:, 1], z=rel[:, 2], mode="lines", name="Moon relative path", line=dict(color="#a78bfa", width=5)))
    idx0 = frame_indices[0]
    fig.add_trace(go.Scatter3d(x=[0], y=[0], z=[0], mode="markers+text", text=["🌍"], textposition="top center", name="Earth", marker=dict(size=12, color="#3b82f6")))
    fig.add_trace(go.Scatter3d(x=[rel[idx0, 0]], y=[rel[idx0, 1]], z=[rel[idx0, 2]], mode="markers+text", text=["🌙"], textposition="top center", name="Moon", marker=dict(size=9, color="#c4b5fd")))
    frames = []
    steps = []
    for idx in frame_indices:
        frames.append(go.Frame(name=f"moon{idx}", data=[go.Scatter3d(x=[rel[idx, 0]], y=[rel[idx, 1]], z=[rel[idx, 2]], mode="markers+text", text=["🌙"], textposition="top center", marker=dict(size=9, color="#c4b5fd"))], traces=[2]))
        steps.append(dict(label=f"{result.times_s[idx] / 86400:.1f} d", method="animate", args=[[f"moon{idx}"], {"mode": "immediate", "frame": {"duration": 0, "redraw": True}, "transition": {"duration": 0}}]))
    fig.frames = frames
    fig.update_layout(
        title="Earth–Moon zoom · distances in 1,000 km",
        margin=dict(l=0, r=0, t=48, b=0), paper_bgcolor="#0d1a2b", plot_bgcolor="#0d1a2b", font=dict(color="#dbeafe"),
        legend=dict(orientation="h", y=1.02, x=0),
        scene=dict(bgcolor="#07111f", aspectmode="data", xaxis=dict(title="ΔX (10³ km)", gridcolor="#233b55"), yaxis=dict(title="ΔY (10³ km)", gridcolor="#233b55"), zaxis=dict(title="ΔZ (10³ km)", gridcolor="#233b55")),
        updatemenus=[dict(type="buttons", showactive=False, x=.02, y=1.08, buttons=[dict(label="▶ Play", method="animate", args=[None, {"fromcurrent": True, "frame": {"duration": 70, "redraw": True}, "transition": {"duration": 0}}]), dict(label="⏸ Pause", method="animate", args=[[None], {"mode": "immediate", "frame": {"duration": 0}}])])],
        sliders=[dict(active=0, x=.16, y=1.06, len=.80, currentvalue={"prefix": "Time: ", "suffix": " days"}, steps=steps)],
    )
    return fig


# -----------------------------------------------------------------------------
# Header
# -----------------------------------------------------------------------------
st.markdown(
    '<div class="hero"><div class="eyebrow">Astrodynamics laboratory</div><h1>🛰️ Orbit Sim</h1>'
    '<p>Explore orbital mechanics through an interactive time-aware simulator, mission-design tools and a separate N-body gravity laboratory.</p></div>',
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# Sidebar: Earth orbit scenario
# -----------------------------------------------------------------------------
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
full_orbits = st.sidebar.slider("Simulation length (orbits)", 0.25, 12.0, 2.0, 0.25)
model = st.sidebar.selectbox("Force model", ["two-body", "j2", "drag"])
dt = st.sidebar.slider("Integrator step (s)", 2, 60, 10)
st.sidebar.divider()
st.sidebar.caption("Initial state: true anomaly ν = 0° at periapsis.")

perigee_radius = R_EARTH_KM + altitude
if eccentricity > 0:
    a = perigee_radius / (1.0 - eccentricity)
else:
    a = perigee_radius
apoapsis_altitude = a * (1.0 + eccentricity) - R_EARTH_KM

if perigee_radius <= R_EARTH_KM or apoapsis_altitude <= 0:
    st.error("This orbit intersects Earth. Increase the perigee altitude or reduce eccentricity.")
    st.stop()

period = orbital_period_from_a(a)
state0 = elements_to_state(OrbitalElements(a, eccentricity, np.deg2rad(inclination), 0.0, 0.0, 0.0))

with st.spinner("Propagating trajectory…"):
    result = propagate(
        state0,
        duration_s=full_orbits * period,
        dt_s=dt,
        model=model,
        density_kg_m3=4e-12,
        ballistic_coeff_m2_kg=0.01,
    )

alts = altitude_km(result.positions_km)
impact = bool(np.any(alts < 0))
if impact:
    st.warning("The propagated trajectory intersects Earth. This educational model is not a re-entry simulator.")


# -----------------------------------------------------------------------------
# Summary cards with explicit units — no truncated '…' values.
# -----------------------------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)
with c1:
    info_card("Semi-major axis", f"{a:,.1f} km", "Distance from Earth's centre")
with c2:
    info_card("Orbital period", f"{period / 60:,.1f} min", "Time for one revolution")
with c3:
    info_card("Perigee → apogee", f"{altitude:,.0f} → {apoapsis_altitude:,.0f} km", "Altitude above Earth's surface")
with c4:
    info_card("Samples", f"{len(result.times_s):,}", f"One state every {dt} s")

st.markdown(
    f'<span class="status">Model: {model} · RK4 · ECI · full simulation: {full_orbits:.2f} orbits · {result.times_s[-1] / 60:.1f} min</span>',
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# Tabs
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(["🚀 Orbit player", "📈 Analysis", "🎯 Mission design", "🌞 N-body lab"])

with tab1:
    st.info("Use **▶ Play** in the graph to watch the spacecraft move. The dark trajectory is the complete future path; the bright path is the portion already travelled.")
    st.plotly_chart(orbit_player_figure(result.positions_km, result.times_s), use_container_width=True, config={"displaylogo": False})
    left, right = st.columns(2)
    lon, lat = ground_track(result.times_s, result.positions_km)
    with left:
        gt = go.Figure(go.Scatter(x=lon, y=lat, mode="lines", line=dict(color="#a78bfa", width=2.5)))
        gt.update_layout(title="Ground track", margin=dict(l=0, r=0, t=45, b=0), paper_bgcolor="#0d1a2b", plot_bgcolor="#07111f", font=dict(color="#dbeafe"), xaxis=dict(title="Longitude (deg)", range=[-180, 180], gridcolor="#233b55"), yaxis=dict(title="Latitude (deg)", range=[-90, 90], gridcolor="#233b55"))
        st.plotly_chart(gt, use_container_width=True, config={"displaylogo": False})
    with right:
        st.plotly_chart(line_chart(result.times_s / 60, alts, "Altitude vs time", "Time (min)", "Altitude (km)"), use_container_width=True, config={"displaylogo": False})

with tab2:
    left, right = st.columns(2)
    with left:
        energies = np.array([specific_energy(s[:3], s[3:]) for s in result.states])
        st.plotly_chart(line_chart(result.times_s / 60, energies, "Specific orbital energy", "Time (min)", "Specific energy (km²/s²)"), use_container_width=True, config={"displaylogo": False})
    with right:
        speeds = np.linalg.norm(result.velocities_km_s, axis=1)
        st.plotly_chart(line_chart(result.times_s / 60, speeds, "Orbital speed", "Time (min)", "Speed (km/s)"), use_container_width=True, config={"displaylogo": False})
    st.subheader("Scenario details")
    table = pd.DataFrame({
        "Parameter": ["Force model", "Integrator", "Step", "Simulation duration", "Inclination", "Eccentricity", "Semi-major axis", "Perigee altitude", "Apogee altitude", "Minimum altitude", "Maximum altitude"],
        "Value": [model, "RK4", f"{dt} s", f"{result.times_s[-1] / 60:.2f} min", f"{inclination:.2f} deg", f"{eccentricity:.4f}", f"{a:.3f} km", f"{altitude:.3f} km", f"{apoapsis_altitude:.3f} km", f"{np.min(alts):.3f} km", f"{np.max(alts):.3f} km"],
    })
    st.dataframe(table, use_container_width=True, hide_index=True)

with tab3:
    st.subheader("Hohmann transfer")
    c1, c2, c3 = st.columns(3)
    r1_alt = c1.number_input("Initial circular altitude", min_value=180.0, value=400.0, step=50.0, format="%.0f")
    r2_alt = c2.number_input("Final circular altitude", min_value=180.0, value=35786.0, step=50.0, format="%.0f")
    h = hohmann_transfer(R_EARTH_KM + r1_alt, R_EARTH_KM + r2_alt)
    c3.metric("Total Δv", f"{h.total_delta_v_km_s:.3f} km/s")
    st.write({"First burn": f"{h.delta_v1_km_s:.3f} km/s", "Second burn": f"{h.delta_v2_km_s:.3f} km/s", "Transfer time": f"{h.transfer_time_s / 3600:.2f} h"})

    st.subheader("Trajectory export")
    df = pd.DataFrame(result.states, columns=["x_km", "y_km", "z_km", "vx_km_s", "vy_km_s", "vz_km_s"])
    df.insert(0, "time_s", result.times_s)
    st.download_button("Download trajectory CSV", data=df.to_csv(index=False).encode("utf-8"), file_name="orbit_trajectory.csv", mime="text/csv")

with tab4:
    st.subheader("Mutual-gravity experiment")
    st.caption("This is a separate N-body model. Each point mass feels the gravity of all the others; the visualisations use different scales so the Moon is visible instead of being flattened into the Sun–Earth distance.")
    nbody_days = st.slider("Simulation duration (days)", 5, 60, 30, 5)
    nbody_dt_h = st.slider("N-body step (hours)", 0.5, 12.0, 2.0, 0.5)
    with st.spinner("Integrating Sun–Earth–Moon…"):
        nbody = sun_earth_moon_demo(duration_days=float(nbody_days), dt_hours=float(nbody_dt_h))

    m1, m2, m3 = st.columns(3)
    m1.metric("Bodies", "3")
    m2.metric("Duration", f"{nbody.times_s[-1] / 86400:.0f} days")
    m3.metric("Step", f"{nbody_dt_h:.1f} h")

    st.plotly_chart(nbody_solar_figure(nbody), use_container_width=True, config={"displaylogo": False})
    st.plotly_chart(nbody_local_figure(nbody), use_container_width=True, config={"displaylogo": False})

    earth_moon_distance = np.linalg.norm(nbody.positions_km[:, 2, :] - nbody.positions_km[:, 1, :], axis=1)
    st.plotly_chart(line_chart(nbody.times_s / 86400, earth_moon_distance, "Earth–Moon separation", "Time (days)", "Separation (km)"), use_container_width=True, config={"displaylogo": False})
    st.warning("N-body is intentionally a transparent educational model: bodies are point masses and the demo uses simplified initial conditions. It is not a high-fidelity ephemeris system.")


st.divider()
st.caption("Orbit Sim is educational/research software. Simplified force and atmosphere models are intended for learning and prototyping, not flight operations.")
