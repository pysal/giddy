import unittest
import libpysal
import libpysal.api as ps
import mapclassify.api as mc
import giddy.api as gapi
import numpy as np

RTOL = 0.00001

class Rose_Tester(unittest.TestCase):
    def setUp(self):
        f = open(libpysal.examples.get_path("spi_download.csv"), 'r')
        lines = f.readlines()
        f.close()
        lines = [line.strip().split(",") for line in lines]
        names = [line[2] for line in lines[1:-5]]
        data = np.array([list(map(int, line[3:])) for line in lines[1:-5]])
        out = ['"United States 3/"',
               '"Alaska 3/"',
               '"District of Columbia"',
               '"Hawaii 3/"',
               '"New England"',
               '"Mideast"',
               '"Great Lakes"',
               '"Plains"',
               '"Southeast"',
               '"Southwest"',
               '"Rocky Mountain"',
               '"Far West 3/"']
        snames = [name for name in names if name not in out]
        sids = [names.index(name) for name in snames]
        states = data[sids, :]
        us = data[0]
        rel = states / (us * 1.)
        gal = libpysal.open(libpysal.examples.get_path('states48.gal'))
        self.w = gal.read()
        self.w.transform = 'r'
        self.Y = rel[:, [0, -1]]

    def test_rose(self):
        k = 4
        np.random.seed(100)
        r4 = gapi.Rose(self.Y, self.w, k)
        exp = [0., 1.57079633, 3.14159265, 4.71238898, 6.28318531]
        obs = list(r4.cuts)
        for i in range(k + 1):
            self.assertAlmostEqual(exp[i], obs[i])
        self.assertEqual(list(r4.counts), [32, 5, 9, 2])


class SteadyState_Tester(unittest.TestCase):
    def setUp(self):
        self.p = np.array([[.5, .25, .25], [.5, 0, .5], [.25, .25, .5]])

    def test_steady_state(self):
        obs = gapi.steady_state(self.p)
        exp = np.array([0.4, 0.2, 0.4])
        np.testing.assert_array_almost_equal(exp, obs)


class Fmpt_Tester(unittest.TestCase):
    def setUp(self):
        self.p = np.array([[.5, .25, .25], [.5, 0, .5], [.25, .25, .5]])

    def test_fmpt(self):
        obs = gapi.fmpt(self.p)
        exp = np.array([[2.5, 4., 3.33333333], [2.66666667, 5.,
                                                2.66666667],
                        [3.33333333, 4., 2.5]])
        np.testing.assert_array_almost_equal(exp, obs)


class VarFmpt_Tester(unittest.TestCase):
    def setUp(self):
        self.p = np.array([[.5, .25, .25], [.5, 0, .5], [.25, .25, .5]])

    def test_var_fmpt(self):
        obs = gapi.var_fmpt(self.p)
        exp = np.array([[5.58333333, 12., 6.88888889], [6.22222222,
                                                         12., 6.22222222], [6.88888889, 12., 5.58333333]])
        np.testing.assert_array_almost_equal(exp, obs)

class test_Markov(unittest.TestCase):
    def test___init__(self):
        # markov = Markov(class_ids, classes)
        f = libpysal.open(libpysal.examples.get_path('usjoin.csv'))
        pci = np.array([f.by_col[str(y)] for y in range(1929, 2010)])
        q5 = np.array([mc.Quantiles(y).yb for y in pci]).transpose()
        m = gapi.Markov(q5)
        expected = np.array([[729., 71., 1., 0., 0.],
                             [72., 567., 80., 3., 0.],
                             [0., 81., 631., 86., 2.],
                             [0., 3., 86., 573., 56.],
                             [0., 0., 1., 57., 741.]])
        np.testing.assert_array_equal(m.transitions, expected)
        expected = np.array([[0.91011236, 0.0886392,
                               0.00124844, 0., 0.],
                              [0.09972299, 0.78531856, 0.11080332, 0.00415512,
                                  0.],
                              [0., 0.10125, 0.78875, 0.1075, 0.0025],
                              [0., 0.00417827, 0.11977716, 0.79805014,
                                  0.07799443],
                              [0., 0., 0.00125156, 0.07133917, 0.92740926]])
        np.testing.assert_array_almost_equal(m.p, expected)
        expected = np.array([0.20774716, 0.18725774, 0.20740537, 0.18821787,
                             0.20937187])
        np.testing.assert_array_almost_equal(m.steady_state, expected)


class test_Spatial_Markov(unittest.TestCase):
    def test___init__(self):
        f = libpysal.open(libpysal.examples.get_path('usjoin.csv'))
        pci = np.array([f.by_col[str(y)] for y in range(1929, 2010)])
        pci = pci.transpose()
        rpci = pci / (pci.mean(axis=0))
        w = libpysal.open(libpysal.examples.get_path("states48.gal")).read()
        w.transform = 'r'

        #continuous case
        sm = gapi.Spatial_Markov(rpci, w, fixed=True, k=5,m=5)
        S = np.array([[0.43509425, 0.2635327, 0.20363044, 0.06841983,
                       0.02932278], [0.13391287, 0.33993305, 0.25153036,
                                     0.23343016, 0.04119356], [0.12124869,
                                                               0.21137444,
                                                               0.2635101,
                                                               0.29013417,
                                                               0.1137326],
                      [0.0776413, 0.19748806, 0.25352636, 0.22480415,
                       0.24654013], [0.01776781, 0.19964349, 0.19009833,
                                     0.25524697, 0.3372434]])
        np.testing.assert_array_almost_equal(S, sm.S)

        # user-defined cutoffs
        cc = np.array([0.8, 0.9, 1, 1.2])
        sm = gapi.Spatial_Markov(rpci, w, cutoffs=cc, lag_cutoffs=cc)
        P = np.array([[[0.96703297, 0.03296703, 0., 0., 0.],
                       [0.10638298, 0.68085106, 0.21276596, 0., 0.],
                       [0., 0.14285714, 0.7755102, 0.08163265, 0.],
                       [0., 0., 0.5, 0.5, 0.],
                       [0., 0., 0., 0., 0.]],

                      [[0.88636364, 0.10606061, 0.00757576, 0., 0.],
                       [0.04402516, 0.89308176, 0.06289308, 0., 0.],
                       [0., 0.05882353, 0.8627451, 0.07843137, 0.],
                       [0., 0., 0.13846154, 0.86153846, 0.],
                       [0., 0., 0., 0., 1.]],

                      [[0.78082192, 0.17808219, 0.02739726, 0.01369863, 0.],
                       [0.03488372, 0.90406977, 0.05813953, 0.00290698, 0.],
                       [0., 0.05919003, 0.84735202, 0.09034268, 0.00311526],
                       [0., 0., 0.05811623, 0.92985972, 0.01202405],
                       [0., 0., 0., 0.14285714, 0.85714286]],

                      [[0.82692308, 0.15384615, 0., 0.01923077, 0.],
                       [0.0703125, 0.7890625, 0.125, 0.015625, 0.],
                       [0.00295858, 0.06213018, 0.82248521, 0.10946746,
                        0.00295858],
                       [0., 0.00185529, 0.07606679, 0.88497217, 0.03710575],
                       [0., 0., 0., 0.07803468, 0.92196532]],

                      [[0., 0., 0., 0., 0.],
                       [0., 0., 0., 0., 0.],
                       [0., 0.06666667, 0.9, 0.03333333, 0.],
                       [0., 0., 0.05660377, 0.90566038, 0.03773585],
                       [0., 0., 0., 0.03932584, 0.96067416]]])
        np.testing.assert_array_almost_equal(P, sm.P)

        #discrete case
        discretized = (rpci * 100).astype(int) % 4
        w = libpysal.weights.Contiguity.Queen.from_shapefile(
            libpysal.examples.get_path('us48.shp'))
        np.random.seed(24788)
        sm = gapi.Spatial_Markov(discretized, w, discrete=True)
        answer = np.array([[[92., 88., 75., 95.],
                            [50., 55., 52., 35.],
                            [45., 48., 58., 48.],
                            [45., 32., 39., 51.]],

                           [[54., 43., 40., 51.],
                            [92., 97., 91., 89.],
                            [44., 49., 56., 55.],
                            [40., 35., 75., 50.]],

                           [[67., 51., 43., 58.],
                            [41., 58., 56., 35.],
                            [86., 88., 140., 89.],
                            [42., 56., 61., 73.]],

                           [[56., 51., 39., 38.],
                            [50., 49., 50., 45.],
                            [41., 61., 55., 46.],
                            [93., 77., 87., 89.]]])

        np.testing.assert_array_equal(sm.T, answer)




class test_LISA_Markov(unittest.TestCase):
    def test___init__(self):
        f = libpysal.open(libpysal.examples.get_path('usjoin.csv'))
        pci = np.array(
            [f.by_col[str(y)] for y in range(1929, 2010)]).transpose()
        w = libpysal.open(libpysal.examples.get_path("states48.gal")).read()
        lm = gapi.LISA_Markov(pci, w)
        obs = np.array([1, 2, 3, 4])
        np.testing.assert_array_almost_equal(obs, lm.classes)
        ss = np.array([0.28561505, 0.14190226, 0.40493672,
                        0.16754598])
        np.testing.assert_array_almost_equal(lm.steady_state, ss)
        transitions = np.array([[1.08700000e+03, 4.40000000e+01,
                                 4.00000000e+00, 3.40000000e+01], [
                                     4.10000000e+01, 4.70000000e+02,
                                     3.60000000e+01, 1.00000000e+00], [
                                         5.00000000e+00, 3.40000000e+01,
                                         1.42200000e+03, 3.90000000e+01], [
                                             3.00000000e+01,   1.00000000e+00,
                                             4.00000000e+01, 5.52000000e+02]])
        np.testing.assert_array_almost_equal(lm.transitions, transitions)
        p = np.array([[0.92985458,  0.03763901,  0.00342173,  0.02908469],
                       [0.07481752, 0.85766423, 0.06569343, 0.00182482],
                       [0.00333333, 0.02266667, 0.948, 0.026], [0.04815409,
                                                                0.00160514,
                                                                0.06420546,
                                                                0.88603531]])
        np.testing.assert_array_almost_equal(lm.p, p)
        np.random.seed(10)
        lm_random = gapi.LISA_Markov(pci, w, permutations=99)
        expected = np.array([[1.12328098e+03,   1.15377356e+01,
                              3.47522158e-01, 3.38337644e+01], [
                                  3.50272664e+00,   5.28473882e+02,
                                  1.59178880e+01, 1.05503814e-01], [
                                      1.53878082e-01,   2.32163556e+01,
                                      1.46690710e+03, 9.72266513e+00], [
                                          9.60775143e+00,   9.86856346e-02,
                                          6.23537392e+00, 6.07058189e+02]])
        np.testing.assert_allclose(lm_random.expected_t, expected, RTOL)
        c = np.array([1058.207904, 0., 9.])
        np.testing.assert_allclose(lm_random.chi_2, c, RTOL)



class test_prais(unittest.TestCase):
    def test___init__(self):
        import numpy as np
        f = libpysal.open(libpysal.examples.get_path('usjoin.csv'))
        pci = np.array([f.by_col[str(y)] for y in range(1929, 2010)])
        q5 = np.array([mc.Quantiles(y).yb for y in pci]).transpose()
        m = gapi.Markov(q5)
        res = np.array([0.08988764, 0.21468144,
                          0.21125, 0.20194986, 0.07259074])
        np.testing.assert_array_almost_equal(gapi.prais(m.p), res)


class Theta_Tester(unittest.TestCase):
    def setUp(self):
        f = libpysal.open(libpysal.examples.get_path('mexico.csv'))
        vnames = ["pcgdp%d" % dec for dec in range(1940, 2010, 10)]
        self.y = np.transpose(np.array([f.by_col[v] for v in vnames]))
        self.regime = np.array(f.by_col['esquivel99'])

    def test_Theta(self):
        np.random.seed(10)
        t = gapi.Theta(self.y, self.regime, 999)
        k = self.y.shape[1]
        obs = t.theta.tolist()
        exp = [[0.41538462, 0.28070175, 0.61363636, 0.62222222,
                0.33333333, 0.47222222]]
        for i in range(k - 1):
            self.assertAlmostEqual(exp[0][i], obs[0][i])
        obs = t.pvalue_left.tolist()
        exp = [0.307, 0.077, 0.823, 0.552, 0.045, 0.735]
        for i in range(k - 1):
            self.assertAlmostEqual(exp[i], obs[i])
        obs = t.total.tolist()
        exp = [130., 114., 88., 90., 90., 72.]
        for i in range(k - 1):
            self.assertAlmostEqual(exp[i], obs[i])
        self.assertEqual(t.max_total, 512)


class SpatialTau_Tester(unittest.TestCase):
    def setUp(self):
        f = libpysal.open(libpysal.examples.get_path('mexico.csv'))
        vnames = ["pcgdp%d" % dec for dec in range(1940, 2010, 10)]
        self.y = np.transpose(np.array([f.by_col[v] for v in vnames]))
        regime = np.array(f.by_col['esquivel99'])
        self.w = ps.block_weights(regime)

    def test_SpatialTau(self):
        np.random.seed(12345)
        k = self.y.shape[1]
        obs = [gapi.SpatialTau(self.y[:, i], self.y[:, i + 1],
                               self.w, 99) for i in range(k - 1)]
        tau_s = [0.397, 0.492, 0.651, 0.714, 0.683, 0.810]
        ev_tau_s = [0.659, 0.706, 0.772, 0.752, 0.705, 0.819]
        p_vals = [0.010, 0.010, 0.020, 0.210, 0.270, 0.280]
        for i in range(k - 1):
            self.assertAlmostEqual(tau_s[i], obs[i].tau_spatial, 3)
            self.assertAlmostEqual(ev_tau_s[i], obs[i].taus.mean(), 3)
            self.assertAlmostEqual(p_vals[i], obs[i].tau_spatial_psim, 3)


class Tau_Tester(unittest.TestCase):
    def test_Tau(self):
        x1 = [12, 2, 1, 12, 2]
        x2 = [1, 4, 7, 1, 0]
        kt = gapi.Tau(x1, x2)
        self.assertAlmostEqual(kt.tau, -0.47140452079103173, 5)
        self.assertAlmostEqual(kt.tau_p, 0.24821309157521476, 5)




suite = unittest.TestSuite()
test_classes = [Rose_Tester, SteadyState_Tester, Fmpt_Tester, VarFmpt_Tester]
for i in test_classes:
    a = unittest.TestLoader().loadTestsFromTestCase(i)
    suite.addTest(a)





if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite)
