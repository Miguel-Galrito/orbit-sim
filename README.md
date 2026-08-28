# 🛰️ Orbit Sim

Interactive orbital mechanics laboratory in Python.

Build, propagate and analyse spacecraft orbits while learning numerical methods, astrodynamics and software engineering.

## ✨ What it can do now

- Classical orbital elements ↔ Cartesian state vectors
- Two-body propagation with RK4
- Earth J2 perturbation
- Rotating-atmosphere drag model
- Impulsive maneuvers
- Hohmann transfers
- Plane-change Δv
- Bi-elliptic transfers
- Universal-variable Lambert solver
- Ground-track, altitude, speed and energy analysis
- Interactive Streamlit + Plotly dashboard
- CSV export from the dashboard
- Automated tests with GitHub Actions

## 🖥️ Run it on your computer

### Windows PowerShell

```powershell
git clone https://github.com/Miguel-Galrito/orbit-sim.git
cd orbit-sim
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
pytest
streamlit run streamlit_app.py
```

### macOS / Linux

```bash
git clone https://github.com/Miguel-Galrito/orbit-sim.git
cd orbit-sim
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
pytest
streamlit run streamlit_app.py
```

Once Streamlit starts, it prints a local URL, normally `http://localhost:8501`. Open that address in your browser.

## ☁️ Publish the dashboard on the internet

Orbit Sim is prepared for Streamlit Community Cloud.

1. Go to `https://share.streamlit.io/` and sign in with GitHub.
2. Connect your GitHub account.
3. Click **Create app**.
4. Select repository `Miguel-Galrito/orbit-sim`, branch `main`, and file `streamlit_app.py`.
5. Click **Deploy**.

Community Cloud creates a shareable `streamlit.app` URL and monitors the linked GitHub repository for updates. The repository includes `requirements.txt` so the dashboard dependencies are installed automatically. citeturn772748search0turn772748search1turn772748search3

## 🧱 Architecture

```text
src/orbitsim/
  constants.py      Physical constants
  types.py          Immutable state/data models
  elements.py       Orbital-element conversions
  dynamics.py       Acceleration models
  propagation.py    RK4 propagator + maneuver events
  maneuvers.py      Transfer and maneuver design
  lambert.py        Universal-variable Lambert solver
  analysis.py       Ground track, altitude and energy helpers
  cli.py            Command-line interface

streamlit_app.py    Interactive mission-analysis dashboard
tests/              Physics and regression tests
```

**Physics first, visualization second.** The numerical core stays independent of Streamlit so it can be reused from tests, scripts, notebooks and future APIs.

## 🧪 Validation philosophy

The project treats numerical checks as first-class engineering work:

- round-trip element/state conversion tests
- two-body specific-energy conservation
- analytical transfer sanity checks
- regression tests for edge cases
- automated test execution in CI

## 🗺️ Roadmap

### Phase 1 — foundation ✅
- [x] Clean package layout
- [x] State and orbital-element models
- [x] RK4 two-body propagation
- [x] Unit-aware documentation and tests

### Phase 2 — realistic Earth model ✅
- [x] J2 perturbation
- [x] Rotating atmosphere + drag term
- [x] Altitude and energy diagnostics
- [x] Ground-track generation

### Phase 3 — mission design ✅
- [x] Hohmann transfers
- [x] Impulsive maneuver events
- [x] Plane-change Δv
- [x] Bi-elliptic transfer model
- [x] Lambert solver

### Phase 4 — interactive engineering tool 🔄
- [x] Interactive 3D Earth view
- [x] Preset mission scenarios
- [x] Live telemetry and diagnostics
- [x] Ground-track and altitude plots
- [x] Mission-design panel
- [x] CSV trajectory export
- [ ] TLE ingestion + SGP4 reference mode
- [ ] Monte Carlo uncertainty propagation
- [ ] Scenario/configuration files
- [ ] Benchmark suite + profiling

### Phase 5 — advanced astrodynamics
- [ ] Higher-order gravity harmonics
- [ ] Higher-fidelity atmosphere adapter
- [ ] Solar radiation pressure
- [ ] Sun/Moon third-body gravity
- [ ] N-body propagation
- [ ] State transition matrices and sensitivity analysis
- [ ] Differential correction / orbit determination

### Phase 6 — mission-analysis platform
- [ ] Ground-station visibility and access windows
- [ ] Sensor / coverage geometry
- [ ] Reproducible mission scenario files
- [ ] Reference validation notebooks
- [ ] Documentation website
- [ ] End-to-end LEO → GEO case study
- [ ] CSV / JSON / Parquet export

### Phase 7 — research / portfolio quality
- [ ] Cross-check selected cases against established astrodynamics libraries
- [ ] Numerical error vs. step-size report
- [ ] Performance benchmark report
- [ ] Multi-version Python CI matrix
- [ ] API documentation generation
- [ ] Release tags + changelog
- [ ] Architecture / design decision records

## ⚠️ Scientific scope

Orbit Sim is educational and research-oriented software, not flight-certified software. Simplified force and atmosphere models are intentionally transparent so that their assumptions can be inspected and tested.

## License

MIT
