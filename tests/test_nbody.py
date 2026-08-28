import numpy as np

from orbitsim.nbody import Body, propagate_nbody


def test_nbody_returns_requested_end_time():
    bodies = (Body("A", 1e12), Body("B", 1e12))
    r0 = np.array([[-500.0, 0.0, 0.0], [500.0, 0.0, 0.0]])
    v0 = np.array([[0.0, -1.0, 0.0], [0.0, 1.0, 0.0]])
    result = propagate_nbody(bodies, r0, v0, duration_s=100.0, dt_s=10.0)
    assert result.times_s[-1] == 100.0
    assert result.positions_km.shape == (11, 2, 3)
    assert np.all(np.isfinite(result.positions_km))
