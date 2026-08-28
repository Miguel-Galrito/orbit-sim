from orbitsim.maneuvers import hohmann_transfer

def test_hohmann_known_scale():
 h=hohmann_transfer(6578.137,42164.0);assert 2.3<h.delta_v1_km_s<2.5;assert 1.4<h.delta_v2_km_s<1.6;assert h.total_delta_v_km_s>3.7
