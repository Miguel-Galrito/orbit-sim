import numpy as np
from orbitsim import bielliptic_transfer, lambert_universal, plane_change_delta_v


def test_plane_change():
    assert np.isclose(plane_change_delta_v(7.5, np.deg2rad(60)), 7.5)


def test_lambert_returns_finite_transfer_velocities():
    r1 = np.array([7000.0, 0.0, 0.0])
    r2 = np.array([0.0, 7000.0, 0.0])
    v1, v2 = lambert_universal(r1, r2, 2700.0)
    assert np.isfinite(v1).all() and np.isfinite(v2).all()


def test_bielliptic_is_positive():
    result = bielliptic_transfer(7000.0, 100000.0, 42000.0)
    assert result.total_delta_v_km_s > 0
    assert result.transfer_time_s > 0
