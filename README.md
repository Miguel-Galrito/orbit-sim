# Orbit Sim

A Python orbital-mechanics laboratory built as a portfolio project: deterministic physics core, numerical propagation, perturbation models, maneuver analysis, tests, CLI, and interactive visualization.

## Current capabilities

- Classical orbital elements ↔ Cartesian state vectors
- Two-body Earth propagation with fixed-step RK4
- J2 oblateness perturbation
- Simple rotating-atmosphere drag model
- Impulsive inertial maneuvers
- Hohmann transfer calculator
- Ground-track and altitude post-processing
- CLI and Streamlit interface
- Automated tests via GitHub Actions

## Architecture

```text
src/orbitsim/
  constants.py      Physical constants
  types.py          Immutable state/data models
  elements.py       Orbital-element conversions
  dynamics.py       Acceleration models
  propagation.py    RK4 propagator + maneuver events
  maneuvers.py      Analytical maneuver utilities
  analysis.py       Ground-track, altitude, energy helpers
  cli.py            Command-line interface
```

The key design rule is **physics first, visualization second**. The engine returns NumPy arrays and small immutable data objects so it can be reused from notebooks, scripts, tests, or a web UI.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pytest
orbit-sim --altitude-km 400 --duration-orbits 2 --model j2
streamlit run streamlit_app.py
```

## Roadmap → project ladder

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
- [ ] Plane-change and bi-elliptic transfers
- [ ] Lambert solver

### Phase 4 — professional tooling
- [ ] 3D interactive Plotly view
- [ ] TLE/SGP4 ingestion
- [ ] Monte Carlo uncertainty propagation
- [ ] Parameter/config files
- [ ] Benchmark suite and performance profiling

### Phase 5 — advanced astrodynamics
- [ ] Higher-order gravity harmonics
- [ ] Better atmosphere models
- [ ] Solar radiation pressure
- [ ] Sun/Moon third-body gravity
- [ ] N-body propagation
- [ ] State transition matrices / sensitivity analysis

### Phase 6 — engineering portfolio layer
- [ ] Coverage/ground-station visibility
- [ ] Mission scenario files
- [ ] Reproducible notebooks
- [ ] Documentation website
- [ ] Example mission: LEO → GEO

## Scientific scope

This is an educational simulator, not flight-certified software. The perturbation and atmospheric models deliberately trade fidelity for transparency and readability.

## License

MIT
