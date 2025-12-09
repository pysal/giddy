import libpysal as ps
import numpy as np
import pytest

from .. import rank


class TestTheta:
    def setup_method(self):
        f = ps.io.open(ps.examples.get_path("mexico.csv"))
        vnames = [f"pcgdp{dec}" for dec in range(1940, 2010, 10)]
        self.y = np.transpose(np.array([f.by_col[v] for v in vnames]))
        self.regime = np.array(f.by_col["esquivel99"])

    def test_defaults(self):
        np.random.seed(10)
        t = rank.Theta(self.y, self.regime, 999)
        k = self.y.shape[1]
        obs = t.theta.tolist()
        exp = [[0.41538462, 0.28070175, 0.61363636, 0.62222222, 0.33333333, 0.47222222]]
        for i in range(k - 1):
            assert pytest.approx(exp[0][i]) == obs[0][i]
        obs = t.pvalue_left.tolist()
        exp = [0.307, 0.077, 0.823, 0.552, 0.045, 0.735]
        for i in range(k - 1):
            assert pytest.approx(exp[i]) == obs[i]
        obs = t.total.tolist()
        exp = [130.0, 114.0, 88.0, 90.0, 90.0, 72.0]
        for i in range(k - 1):
            assert pytest.approx(exp[i]) == obs[i]
        assert t.max_total == 512


class TestSpatialTau:
    def setup_method(self):
        f = ps.io.open(ps.examples.get_path("mexico.csv"))
        vnames = [f"pcgdp{dec}" for dec in range(1940, 2010, 10)]
        self.y = np.transpose(np.array([f.by_col[v] for v in vnames]))
        regime = np.array(f.by_col["esquivel99"])
        self.w = ps.weights.block_weights(regime)

    def test_defaults(self):
        np.random.seed(12345)
        k = self.y.shape[1]
        obs = [
            rank.SpatialTau(self.y[:, i], self.y[:, i + 1], self.w, 99)
            for i in range(k - 1)
        ]
        tau_s = [0.397, 0.492, 0.651, 0.714, 0.683, 0.810]
        ev_tau_s = [0.659, 0.706, 0.772, 0.752, 0.705, 0.819]
        p_vals = [0.010, 0.010, 0.020, 0.210, 0.270, 0.280]
        for i in range(k - 1):
            assert pytest.approx(tau_s[i], 3) == obs[i].tau_spatial
            assert pytest.approx(ev_tau_s[i], 3) == obs[i].taus.mean()
            assert pytest.approx(p_vals[i], 3) == obs[i].tau_spatial_psim
        st12 = rank.SpatialTau(self.y[:, 1], self.y[:, 2], self.w)
        st21 = rank.SpatialTau(self.y[:, 2], self.y[:, 1], self.w)
        assert pytest.approx(st12.tau_spatial) == st21.tau_spatial


class TestTau:
    def test_defaults(self):
        x1 = [12, 2, 1, 12, 2]
        x2 = [1, 4, 7, 1, 0]
        kt = rank.Tau(x1, x2)
        assert pytest.approx(kt.tau, 5) == -0.47140452079103173
        assert pytest.approx(kt.tau_p, 5) == 0.24821309157521476
        x1 = [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1]
        x2 = [1, 4, 7, 1, 1, 3, 1, 6, 7, 7, 3, 6, 2, 7, 2, 8]
        kt12 = rank.Tau(x1, x2)
        kt21 = rank.Tau(x2, x1)
        assert kt12.tau == kt21.tau
        assert pytest.approx(kt12.tau) == 0.15494494670022804
