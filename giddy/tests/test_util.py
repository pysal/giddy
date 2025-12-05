import numpy as np

from .. import util


class TestShuffleMatrix:
    def setup_method(self):
        self.X = np.arange(16)
        self.X.shape = (4, 4)

    def test_shuffle_matrix(self):
        np.random.seed(10)
        obs = util.shuffle_matrix(self.X, list(range(4))).flatten().tolist()
        exp = [10, 8, 11, 9, 2, 0, 3, 1, 14, 12, 15, 13, 6, 4, 7, 5]
        for i in range(16):
            assert exp[i] == obs[i]


class TestGetLower:
    def setup_method(self):
        self.X = np.arange(16)
        self.X.shape = (4, 4)

    def test_get_lower(self):
        np.random.seed(10)
        obs = util.get_lower(self.X).flatten().tolist()
        exp = [4, 8, 9, 12, 13, 14]
        for i in range(6):
            assert exp[i] == obs[i]


class TestFillDiagonal:
    def setup_method(self):
        self.p3 = np.array([[0.5, 0.5, 0], [0.3, 0.7, 0], [0, 0, 0]])
        self.p23 = np.array(
            [
                [[0.5, 0.5, 0], [0.3, 0.7, 0], [0, 0, 0]],
                [[0, 0, 0], [0.3, 0.7, 0], [0, 0, 0]],
            ]
        )

    # def test_fill_diag2(self):
    #     obs = util.fill_empty_diagonal_2d(self.p3)
    #     exp = np.array([[0.5, 0.5, 0. ], [0.3, 0.7, 0. ], [0. , 0. , 1. ]])
    #     np.testing.assert_array_almost_equal(exp, obs)
    #
    #     with self.assertRaises(ValueError):
    #         obs = util.fill_empty_diagonal_2d(self.p23)
    #
    # def test_fill_diag3(self):
    #     obs = util.fill_empty_diagonal_3d(self.p23)
    #     exp = np.array([[[0.5, 0.5, 0. ], [0.3, 0.7, 0. ], [0. , 0. , 1. ]],
    #                     [[1. , 0. , 0. ], [0.3, 0.7, 0. ], [0. , 0. , 1. ]]])
    #     np.testing.assert_array_almost_equal(exp, obs)
    #
    #     with self.assertRaises(ValueError):
    #         obs = util.fill_empty_diagonal_3d(self.p3)

    def test_fill_diag(self):
        obs = util.fill_empty_diagonals(self.p3)
        exp = np.array([[0.5, 0.5, 0.0], [0.3, 0.7, 0.0], [0.0, 0.0, 1.0]])
        np.testing.assert_array_almost_equal(exp, obs)

        obs = util.fill_empty_diagonals(self.p23)
        exp = np.array(
            [
                [[0.5, 0.5, 0.0], [0.3, 0.7, 0.0], [0.0, 0.0, 1.0]],
                [[1.0, 0.0, 0.0], [0.3, 0.7, 0.0], [0.0, 0.0, 1.0]],
            ]
        )
        np.testing.assert_array_almost_equal(exp, obs)
