import unittest
import libpysal as ps
import numpy as np
import mapclassify as mc
from ..markov import (
    Markov,
    kullback,
    prais,
    Spatial_Markov,
    LISA_Markov,
    FullRank_Markov,
    sojourn_time,
    GeoRank_Markov,
)

RTOL = 0.00001


class test_Markov(unittest.TestCase):
    def test___init__(self):
        # markov = Markov(class_ids, classes)
        f = ps.io.open(ps.examples.get_path("usjoin.csv"))
        pci = np.array([f.by_col[str(y)] for y in range(1929, 2010)])
        q5 = np.array([mc.Quantiles(y).yb for y in pci]).transpose()
        m = Markov(q5)
        expected = np.array(
            [
                [729.0, 71.0, 1.0, 0.0, 0.0],
                [72.0, 567.0, 80.0, 3.0, 0.0],
                [0.0, 81.0, 631.0, 86.0, 2.0],
                [0.0, 3.0, 86.0, 573.0, 56.0],
                [0.0, 0.0, 1.0, 57.0, 741.0],
            ]
        )
        np.testing.assert_array_equal(m.transitions, expected)
        expected = np.array(
            [
                [0.91011236, 0.0886392, 0.00124844, 0.0, 0.0],
                [0.09972299, 0.78531856, 0.11080332, 0.00415512, 0.0],
                [0.0, 0.10125, 0.78875, 0.1075, 0.0025],
                [0.0, 0.00417827, 0.11977716, 0.79805014, 0.07799443],
                [0.0, 0.0, 0.00125156, 0.07133917, 0.92740926],
            ]
        )
        np.testing.assert_array_almost_equal(m.p, expected)
        expected = np.array(
            [0.20774716, 0.18725774, 0.20740537, 0.18821787, 0.20937187]
        )
        np.testing.assert_array_almost_equal(m.steady_state, expected)

        expected = np.array(
            [
                [4.81354357, 11.50292712, 29.60921231, 53.38594954, 103.59816743],
                [42.04774505, 5.34023324, 18.74455332, 42.50023268, 92.71316899],
                [69.25849753, 27.21075248, 4.82147603, 25.27184624, 75.43305672],
                [84.90689329, 42.85914824, 17.18082642, 5.31299186, 51.60953369],
                [98.41295543, 56.36521038, 30.66046735, 14.21158356, 4.77619083],
            ]
        )
        np.testing.assert_array_almost_equal(m.mfpt, expected)

        expected = np.array([11.125, 4.65806452, 4.73372781, 4.95172414, 13.77586207])
        np.testing.assert_array_almost_equal(m.sojourn_time, expected)

        m = Markov(q5[:, :2])
        expected = np.array(
            [
                [10.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 8.0, 1.0, 0.0, 0.0],
                [0.0, 1.0, 9.0, 1.0, 0.0],
                [0.0, 0.0, 0.0, 8.0, 0.0],
                [0.0, 0.0, 0.0, 1.0, 9.0],
            ]
        )
        np.testing.assert_array_equal(m.transitions, expected)
        expected = np.array(
            [
                [1.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.88888889, 0.11111111, 0.0, 0.0],
                [0.0, 0.09090909, 0.81818182, 0.09090909, 0.0],
                [0.0, 0.0, 0.0, 1.0, 0.0],
                [0.0, 0.0, 0.0, 0.1, 0.9],
            ]
        )
        np.testing.assert_array_almost_equal(m.p, expected)
        expected = np.array([[1.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 1.0, 0.0]])
        np.testing.assert_array_almost_equal(m.steady_state, expected)

        expected = np.array(
            [
                [1.0, np.inf, np.inf, np.inf, np.inf],
                [np.inf, np.inf, 9.0, 29.0, np.inf],
                [np.inf, np.inf, np.inf, 20, np.inf],
                [np.inf, np.inf, np.inf, 1.0, np.inf],
                [np.inf, np.inf, np.inf, 10, np.inf],
            ]
        )
        np.testing.assert_array_almost_equal(m.mfpt, expected)

        expected = np.array([np.inf, 9.0, 5.5, np.inf, 10.0])
        np.testing.assert_array_almost_equal(m.sojourn_time, expected)

        q5_fix = np.array(mc.Quantiles(pci.flatten()).yb).reshape(pci.shape)
        m = Markov(q5_fix[:30, -4:-2], classes=np.arange(5))
        expected = np.array([np.inf, 2.14285714, 1.0, np.inf, np.inf])
        np.testing.assert_array_almost_equal(m.sojourn_time, expected)


class test_Spatial_Markov(unittest.TestCase):
    def setUp(self):
        f = ps.io.open(ps.examples.get_path("usjoin.csv"))
        pci = np.array([f.by_col[str(y)] for y in range(1929, 2010)])
        pci = pci.transpose()
        self.rpci = pci / (pci.mean(axis=0))
        self.discretized = (self.rpci * 100).astype(int) % 4
        self.w = ps.io.open(ps.examples.get_path("states48.gal")).read()
        self.w.transform = "r"

    def test___init__(self):
        sm = Spatial_Markov(self.rpci, self.w, fixed=True, k=5, m=5)
        S = np.array(
            [
                [0.43509425, 0.2635327, 0.20363044, 0.06841983, 0.02932278],
                [0.13391287, 0.33993305, 0.25153036, 0.23343016, 0.04119356],
                [0.12124869, 0.21137444, 0.2635101, 0.29013417, 0.1137326],
                [0.0776413, 0.19748806, 0.25352636, 0.22480415, 0.24654013],
                [0.01776781, 0.19964349, 0.19009833, 0.25524697, 0.3372434],
            ]
        )
        np.testing.assert_array_almost_equal(S, sm.S)
        F0 = np.array(
            [
                [2.29835259, 28.95614035, 46.14285714, 80.80952381, 279.42857143],
                [33.86549708, 3.79459555, 22.57142857, 57.23809524, 255.85714286],
                [43.60233918, 9.73684211, 4.91085714, 34.66666667, 233.28571429],
                [46.62865497, 12.76315789, 6.25714286, 14.61564626, 198.61904762],
                [52.62865497, 18.76315789, 12.25714286, 6.0, 34.1031746],
            ]
        )
        np.testing.assert_array_almost_equal(F0, sm.F[0])

    def test_cutoff(self):
        cc = np.array([0.8, 0.9, 1, 1.2])
        sm = Spatial_Markov(self.rpci, self.w, cutoffs=cc, lag_cutoffs=cc)
        P = np.array(
            [
                [
                    [0.96703297, 0.03296703, 0.0, 0.0, 0.0],
                    [0.10638298, 0.68085106, 0.21276596, 0.0, 0.0],
                    [0.0, 0.14285714, 0.7755102, 0.08163265, 0.0],
                    [0.0, 0.0, 0.5, 0.5, 0.0],
                    [0.0, 0.0, 0.0, 0.0, 0.0],
                ],
                [
                    [0.88636364, 0.10606061, 0.00757576, 0.0, 0.0],
                    [0.04402516, 0.89308176, 0.06289308, 0.0, 0.0],
                    [0.0, 0.05882353, 0.8627451, 0.07843137, 0.0],
                    [0.0, 0.0, 0.13846154, 0.86153846, 0.0],
                    [0.0, 0.0, 0.0, 0.0, 1.0],
                ],
                [
                    [0.78082192, 0.17808219, 0.02739726, 0.01369863, 0.0],
                    [0.03488372, 0.90406977, 0.05813953, 0.00290698, 0.0],
                    [0.0, 0.05919003, 0.84735202, 0.09034268, 0.00311526],
                    [0.0, 0.0, 0.05811623, 0.92985972, 0.01202405],
                    [0.0, 0.0, 0.0, 0.14285714, 0.85714286],
                ],
                [
                    [0.82692308, 0.15384615, 0.0, 0.01923077, 0.0],
                    [0.0703125, 0.7890625, 0.125, 0.015625, 0.0],
                    [0.00295858, 0.06213018, 0.82248521, 0.10946746, 0.00295858],
                    [0.0, 0.00185529, 0.07606679, 0.88497217, 0.03710575],
                    [0.0, 0.0, 0.0, 0.07803468, 0.92196532],
                ],
                [
                    [0.0, 0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.06666667, 0.9, 0.03333333, 0.0],
                    [0.0, 0.0, 0.05660377, 0.90566038, 0.03773585],
                    [0.0, 0.0, 0.0, 0.03932584, 0.96067416],
                ],
            ]
        )
        np.testing.assert_array_almost_equal(P, sm.P)

        ## staying probability of a state is 1 if there is no transition from
        # that state
        sm = Spatial_Markov(
            self.rpci, self.w, cutoffs=cc, lag_cutoffs=cc, fill_empty_classes=True
        )
        P = np.array(
            [
                [
                    [0.96703297, 0.03296703, 0.0, 0.0, 0.0],
                    [0.10638298, 0.68085106, 0.21276596, 0.0, 0.0],
                    [0.0, 0.14285714, 0.7755102, 0.08163265, 0.0],
                    [0.0, 0.0, 0.5, 0.5, 0.0],
                    [0.0, 0.0, 0.0, 0.0, 1.0],
                ],
                [
                    [0.88636364, 0.10606061, 0.00757576, 0.0, 0.0],
                    [0.04402516, 0.89308176, 0.06289308, 0.0, 0.0],
                    [0.0, 0.05882353, 0.8627451, 0.07843137, 0.0],
                    [0.0, 0.0, 0.13846154, 0.86153846, 0.0],
                    [0.0, 0.0, 0.0, 0.0, 1.0],
                ],
                [
                    [0.78082192, 0.17808219, 0.02739726, 0.01369863, 0.0],
                    [0.03488372, 0.90406977, 0.05813953, 0.00290698, 0.0],
                    [0.0, 0.05919003, 0.84735202, 0.09034268, 0.00311526],
                    [0.0, 0.0, 0.05811623, 0.92985972, 0.01202405],
                    [0.0, 0.0, 0.0, 0.14285714, 0.85714286],
                ],
                [
                    [0.82692308, 0.15384615, 0.0, 0.01923077, 0.0],
                    [0.0703125, 0.7890625, 0.125, 0.015625, 0.0],
                    [0.00295858, 0.06213018, 0.82248521, 0.10946746, 0.00295858],
                    [0.0, 0.00185529, 0.07606679, 0.88497217, 0.03710575],
                    [0.0, 0.0, 0.0, 0.07803468, 0.92196532],
                ],
                [
                    [1.0, 0.0, 0.0, 0.0, 0.0],
                    [0.0, 1.0, 0.0, 0.0, 0.0],
                    [0.0, 0.06666667, 0.9, 0.03333333, 0.0],
                    [0.0, 0.0, 0.05660377, 0.90566038, 0.03773585],
                    [0.0, 0.0, 0.0, 0.03932584, 0.96067416],
                ],
            ]
        )
        np.testing.assert_array_almost_equal(P, sm.P)

        S0 = np.array(
            [
                [0.54148249, 0.16780007, 0.24991499, 0.04080245, 0.0],
                [0.0, 0.0, 0.0, 0.0, 1.0],
            ]
        )
        np.testing.assert_array_almost_equal(S0, sm.S[0])

    def test_discretized(self):
        w = ps.weights.Queen.from_shapefile(ps.examples.get_path("us48.shp"))
        np.random.seed(24788)
        sm = Spatial_Markov(self.discretized, w, discrete=True)
        answer = np.array(
            [
                [
                    [92.0, 88.0, 75.0, 95.0],
                    [50.0, 55.0, 52.0, 35.0],
                    [45.0, 48.0, 58.0, 48.0],
                    [45.0, 32.0, 39.0, 51.0],
                ],
                [
                    [54.0, 43.0, 40.0, 51.0],
                    [92.0, 97.0, 91.0, 89.0],
                    [44.0, 49.0, 56.0, 55.0],
                    [40.0, 35.0, 75.0, 50.0],
                ],
                [
                    [67.0, 51.0, 43.0, 58.0],
                    [41.0, 58.0, 56.0, 35.0],
                    [86.0, 88.0, 140.0, 89.0],
                    [42.0, 56.0, 61.0, 73.0],
                ],
                [
                    [56.0, 51.0, 39.0, 38.0],
                    [50.0, 49.0, 50.0, 45.0],
                    [41.0, 61.0, 55.0, 46.0],
                    [93.0, 77.0, 87.0, 89.0],
                ],
            ]
        )

        np.testing.assert_array_equal(sm.T, answer)


class test_chi2(unittest.TestCase):
    def test_chi2(self):
        f = ps.io.open(ps.examples.get_path("usjoin.csv"))
        pci = np.array([f.by_col[str(y)] for y in range(1929, 2010)])
        pci = pci.transpose()
        rpci = pci / (pci.mean(axis=0))
        w = ps.io.open(ps.examples.get_path("states48.gal")).read()
        w.transform = "r"
        sm = Spatial_Markov(rpci, w, fixed=True, k=5, m=5)
        chi = np.array(
            [
                [4.05598541e01, 6.44644317e-04, 1.60000000e01],
                [5.54751974e01, 2.97033748e-06, 1.60000000e01],
                [1.77528996e01, 3.38563882e-01, 1.60000000e01],
                [4.00390961e01, 7.68422046e-04, 1.60000000e01],
                [4.67966803e01, 7.32512065e-05, 1.60000000e01],
            ]
        )
        obs = np.array(sm.chi2)
        np.testing.assert_array_almost_equal(obs, chi)
        obs = np.array(
            [
                [4.61209613e02, 0.00000000e00, 4.00000000e00],
                [1.48140694e02, 0.00000000e00, 4.00000000e00],
                [6.33129261e01, 5.83089133e-13, 4.00000000e00],
                [7.22778509e01, 7.54951657e-15, 4.00000000e00],
                [2.32659201e02, 0.00000000e00, 4.00000000e00],
            ]
        )
        np.testing.assert_array_almost_equal(obs, np.array(sm.shtest))


class test_LISA_Markov(unittest.TestCase):
    def test___init__(self):
        f = ps.io.open(ps.examples.get_path("usjoin.csv"))
        pci = np.array([f.by_col[str(y)] for y in range(1929, 2010)]).transpose()
        w = ps.io.open(ps.examples.get_path("states48.gal")).read()
        lm = LISA_Markov(pci, w)
        obs = np.array([1, 2, 3, 4])
        np.testing.assert_array_almost_equal(obs, lm.classes)
        ss = np.array([0.28561505, 0.14190226, 0.40493672, 0.16754598])
        np.testing.assert_array_almost_equal(lm.steady_state, ss)
        transitions = np.array(
            [
                [1.08700000e03, 4.40000000e01, 4.00000000e00, 3.40000000e01],
                [4.10000000e01, 4.70000000e02, 3.60000000e01, 1.00000000e00],
                [5.00000000e00, 3.40000000e01, 1.42200000e03, 3.90000000e01],
                [3.00000000e01, 1.00000000e00, 4.00000000e01, 5.52000000e02],
            ]
        )
        np.testing.assert_array_almost_equal(lm.transitions, transitions)
        p = np.array(
            [
                [0.92985458, 0.03763901, 0.00342173, 0.02908469],
                [0.07481752, 0.85766423, 0.06569343, 0.00182482],
                [0.00333333, 0.02266667, 0.948, 0.026],
                [0.04815409, 0.00160514, 0.06420546, 0.88603531],
            ]
        )
        np.testing.assert_array_almost_equal(lm.p, p)
        np.random.seed(10)
        lm_random = LISA_Markov(pci, w, permutations=99)
        expected = np.array(
            [
                [1.12328098e03, 1.15377356e01, 3.47522158e-01, 3.38337644e01],
                [3.50272664e00, 5.28473882e02, 1.59178880e01, 1.05503814e-01],
                [1.53878082e-01, 2.32163556e01, 1.46690710e03, 9.72266513e00],
                [9.60775143e00, 9.86856346e-02, 6.23537392e00, 6.07058189e02],
            ]
        )
        np.testing.assert_allclose(lm_random.expected_t, expected, RTOL)
        c = np.array([1058.207904, 0.0, 9.0])
        np.testing.assert_allclose(lm_random.chi_2, c, RTOL)


class test_kullback(unittest.TestCase):
    def test___init__(self):
        s1 = np.array(
            [
                [22, 11, 24, 2, 2, 7],
                [5, 23, 15, 3, 42, 6],
                [4, 21, 190, 25, 20, 34],
                [0, 2, 14, 56, 14, 28],
                [32, 15, 20, 10, 56, 14],
                [5, 22, 31, 18, 13, 134],
            ]
        )
        s2 = np.array(
            [
                [3, 6, 9, 3, 0, 8],
                [1, 9, 3, 12, 27, 5],
                [2, 9, 208, 32, 5, 18],
                [0, 14, 32, 108, 40, 40],
                [22, 14, 9, 26, 224, 14],
                [1, 5, 13, 53, 13, 116],
            ]
        )

        F = np.array([s1, s2])
        res = kullback(F)
        np.testing.assert_array_almost_equal(
            160.96060031170782, res["Conditional homogeneity"]
        )
        dof = res["Conditional homogeneity dof"]
        np.testing.assert_array_almost_equal(30, dof)
        p_value = res["Conditional homogeneity pvalue"]
        np.testing.assert_array_almost_equal(0.0, p_value)


class test_prais(unittest.TestCase):
    def test___init__(self):
        f = ps.io.open(ps.examples.get_path("usjoin.csv"))
        pci = np.array([f.by_col[str(y)] for y in range(1929, 2010)])
        q5 = np.array([mc.Quantiles(y).yb for y in pci]).transpose()
        m = Markov(q5)
        res = np.array([0.08988764, 0.21468144, 0.21125, 0.20194986, 0.07259074])
        np.testing.assert_array_almost_equal(prais(m.p), res)


class FullRank_Markov_Tester(unittest.TestCase):
    def test___init__(self):
        f = ps.io.open(ps.examples.get_path("usjoin.csv"))
        pci = np.array([f.by_col[str(y)] for y in range(1929, 2010)]).transpose()
        m = FullRank_Markov(pci)
        expected = np.array(
            [
                45,
                24,
                46,
                4,
                20,
                3,
                2,
                31,
                43,
                32,
                5,
                22,
                28,
                30,
                40,
                38,
                23,
                13,
                7,
                10,
                25,
                47,
                21,
                27,
                26,
                9,
                15,
                6,
                39,
                1,
                44,
                41,
                12,
                35,
                18,
                11,
                8,
                48,
                37,
                42,
                33,
                29,
                19,
                36,
                14,
                34,
                17,
                16,
            ]
        )
        np.testing.assert_array_equal(m.ranks[:, 0], expected)
        expected = np.array(
            [
                66.0,
                8.0,
                2.0,
                1.0,
                1.0,
                2.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
            ]
        )
        np.testing.assert_array_almost_equal(m.transitions[:, 0], expected)
        expected = np.array(
            [
                0.825,
                0.6375,
                0.55,
                0.4375,
                0.4,
                0.425,
                0.35,
                0.35,
                0.35,
                0.3,
                0.3,
                0.3625,
                0.35,
                0.2875,
                0.225,
                0.175,
                0.2375,
                0.275,
                0.225,
                0.2,
                0.1375,
                0.1125,
                0.2,
                0.15,
                0.1625,
                0.075,
                0.1625,
                0.2,
                0.2,
                0.125,
                0.25,
                0.2125,
                0.2,
                0.275,
                0.3,
                0.2375,
                0.2125,
                0.2,
                0.2375,
                0.2,
                0.1625,
                0.2,
                0.35,
                0.375,
                0.4625,
                0.5,
                0.675,
                0.9625,
            ]
        )
        np.testing.assert_array_almost_equal(m.p.diagonal(), expected)
        expected = np.array(
            [
                48.0,
                225.92564594,
                271.55443692,
                302.87799868,
                333.42179417,
                374.21580987,
                426.47219884,
                483.53240947,
                511.26683305,
                533.22661693,
                543.81107061,
                563.27715414,
                579.45351872,
                596.25588041,
                604.82361556,
                616.40151207,
                625.31101556,
                632.96110086,
                640.6957394,
                643.33238787,
                643.71256647,
                648.50366743,
                652.26839484,
                651.72983865,
                654.91433128,
                657.45876076,
                660.39021071,
                664.37167639,
                658.72091238,
                670.1547569,
                675.01030372,
                676.67416815,
                682.25590553,
                685.06608009,
                690.00725885,
                699.6945703,
                704.22342186,
                707.21163247,
                710.650161,
                713.4234693,
                714.95522965,
                717.08496941,
                718.07040543,
                719.28902106,
                724.40383642,
                727.11189921,
                730.40467469,
                754.8761577,
            ]
        )
        np.testing.assert_array_almost_equal(m.mfpt[:, 0], expected)
        expected = np.array(
            [
                5.71428571,
                2.75862069,
                2.22222222,
                1.77777778,
                1.66666667,
                1.73913043,
                1.53846154,
                1.53846154,
                1.53846154,
                1.42857143,
                1.42857143,
                1.56862745,
                1.53846154,
                1.40350877,
                1.29032258,
                1.21212121,
                1.31147541,
                1.37931034,
                1.29032258,
                1.25,
                1.15942029,
                1.12676056,
                1.25,
                1.17647059,
                1.19402985,
                1.08108108,
                1.19402985,
                1.25,
                1.25,
                1.14285714,
                1.33333333,
                1.26984127,
                1.25,
                1.37931034,
                1.42857143,
                1.31147541,
                1.26984127,
                1.25,
                1.31147541,
                1.25,
                1.19402985,
                1.25,
                1.53846154,
                1.6,
                1.86046512,
                2.0,
                3.07692308,
                26.66666667,
            ]
        )
        np.testing.assert_array_almost_equal(m.sojourn_time, expected)


class GeoRank_Markov_Tester(unittest.TestCase):
    def test___init__(self):
        f = ps.io.open(ps.examples.get_path("usjoin.csv"))
        pci = np.array([f.by_col[str(y)] for y in range(1929, 2010)]).transpose()
        gm = GeoRank_Markov(pci)
        expected = np.array([38.0, 0.0, 6.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 3.0])
        np.testing.assert_array_almost_equal(gm.transitions[:10, 0], expected)
        expected = np.array(
            [0.475, 0.1875, 0.55, 0.425, 0.1375, 0.7375, 0.4125, 0.2, 0.2375, 0.1]
        )
        np.testing.assert_array_almost_equal(gm.p.diagonal()[:10], expected)
        expected = np.array(
            [
                48.0,
                108.25928005,
                76.96801786,
                122.39954444,
                116.18226087,
                126.19058109,
                122.35062239,
                111.70536817,
                103.91572935,
                99.71598303,
            ]
        )
        np.testing.assert_array_almost_equal(gm.mfpt[:10, 0], expected)
        expected = np.array(
            [
                1.9047619,
                1.23076923,
                2.22222222,
                1.73913043,
                1.15942029,
                3.80952381,
                1.70212766,
                1.25,
                1.31147541,
                1.11111111,
            ]
        )
        np.testing.assert_array_almost_equal(gm.sojourn_time[:10], expected)


class Sojourn_time_Tester(unittest.TestCase):
    def setUp(self):
        self.p = np.array([[0.5, 0.25, 0.25], [0.5, 0, 0.5], [0.25, 0.25, 0.5]])
        self.p2 = np.array([[0.5, 0.5, 0], [0.3, 0.7, 0], [0, 0, 1]])

    def test_sojourn_time(self):
        obs = sojourn_time(self.p)
        exp = np.array([2.0, 1.0, 2.0])
        np.testing.assert_array_almost_equal(exp, obs)

        exp = np.array([2.0, 3.33333333, np.inf])
        np.testing.assert_array_almost_equal(exp, sojourn_time(self.p2))


if __name__ == "__main__":
    unittest.main()
