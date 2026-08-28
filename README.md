# Orbit Sim

A Python orbital-mechanics laboratory designed as a serious engineering portfolio project.

## Current capabilities

- Classical orbital elements ↔ Cartesian state vectors
- Two-body Earth propagation with fixed-step RK4
- J2 oblateness perturbation
- Rotating-atmosphere drag model
- Impulsive maneuver events
- Hohmann, plane-change and bi-elliptic transfer analysis
- Zero-revolution universal-variable Lambert solver
- Ground-track, altitude and energy diagnostics
- CLI and Streamlit visualization
- Automated tests via GitHub Actions

## Architecture

```text
src/orbitsim/
  constants.py      Physical constants
  types.py          Immutable state/data models
  elements.py       Orbital-element conversions
  dynamics.py       Acceleration models
  propagation.py    RK4 propagator + maneuver events
  maneuvers.py      Analytical transfer / maneuver design
  lambert.py        Universal-variable Lambert solver
  analysis.py       Ground track, altitude and energy helpers
  cli.py            Command-line interface
```

The design rule is **physics first, visualization second**. The core returns NumPy arrays and small data objects so the same engine can run from tests, scripts, notebooks or a UI.

## Quick start

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m pip install pytest
pytest
orbit-sim --altitude-km 400 --duration-orbits 2 --model j2
streamlit run streamlit_app.py
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m pip install pytest
pytest
orbit-sim --altitude-km 400 --duration-orbits 2 --model j2
streamlit run streamlit_app.py
```

`venv` creates a separate Python environment for the project, which keeps its dependencies isolated from the rest of the machine.

## Example

```python
import numpy as np
from orbitsim import OrbitalElements, elements_to_state, propagate

state0 = elements_to_state(OrbitalElements(
    a_km=6778.137,
    e=0.001,
    i_rad=np.deg2rad(51.6),
    raan_rad=0.0,
    arg_perigee_rad=0.0,
    true_anomaly_rad=0.0,
))

result = propagate(state0, duration_s=3*5400, dt_s=10, model="j2")
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
- [x] Plane-change and bi-elliptic transfers
- [x] Lambert solver

### Phase 4 — professional tooling
- [ ] Interactive 3D Plotly view
- [ ] TLE ingestion + SGP4 truth/reference mode
- [ ] Monte Carlo uncertainty propagation
- [ ] Scenario/configuration files
- [ ] Benchmark suite + profiling
- [ ] Better error handling and typed public API

### Phase 5 — advanced astrodynamics
- [ ] Higher-order gravity harmonics
- [ ] NRLMSISE/JB2008-compatible atmosphere adapter
- [ ] Solar radiation pressure
- [ ] Sun/Moon third-body gravity
- [ ] N-body propagation
- [ ] State transition matrices and sensitivity analysis
- [ ] Differential correction / orbit determination

### Phase 6 — mission-analysis platform
- [ ] Ground-station visibility and access windows
- [ ] Sensor/coverage geometry
- [ ] Mission scenario files with reproducible parameters
- [ ] Reference notebooks and validation cases
- [ ] Documentation website
- [ ] End-to-end LEO → GEO mission case study
- [ ] Export to CSV/JSON/Parquet

### Phase 7 — portfolio / research quality
- [ ] Compare against poliastro / Orekit reference cases
- [ ] Numerical accuracy report versus step size
- [ ] Performance benchmark report
- [ ] Continuous integration across supported Python versions
- [ ] API documentation generation
- [ ] Release tags and changelog

## Scientific scope

This is educational and research-oriented software, not flight-certified software. Current perturbation models intentionally trade fidelity for transparency and testability. High-fidelity extensions are planned behind stable interfaces so the simple models remain useful for learning and regression tests.

## License

MIT
