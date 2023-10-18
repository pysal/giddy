"""
Utilities for the spatial dynamics module.
"""

__all__ = ["shuffle_matrix", "get_lower", "fill_empty_diagonals"]

import copy

import numpy as np


def shuffle_matrix(X, ids):
    """
    Random permutation of rows and columns of a matrix

    Parameters
    ----------
    X   : array
          (k, k), array to be permutated.
    ids : array
          range (k, ).

    Returns
    -------
    X   : array
          (k, k) with rows and columns randomly shuffled.

    Examples
    --------
    >>> import numpy as np
    >>> from giddy.util import shuffle_matrix
    >>> X=np.arange(16)
    >>> X.shape=(4,4)
    >>> np.random.seed(10)
    >>> shuffle_matrix(X,list(range(4)))
    array([[10,  8, 11,  9],
           [ 2,  0,  3,  1],
           [14, 12, 15, 13],
           [ 6,  4,  7,  5]])

    """
    np.random.shuffle(ids)
    return X[ids, :][:, ids]


def get_lower(matrix):
    """
    Flattens the lower part of an n x n matrix into an n*(n-1)/2 x 1 vector.

    Parameters
    ----------
    matrix  : array
              (n, n) numpy array, a distance matrix.

    Returns
    -------
    lowvec  : array
              numpy array, the lower half of the distance matrix flattened into
              a vector of length n*(n-1)/2.

    Examples
    --------
    >>> import numpy as np
    >>> from giddy.util import get_lower
    >>> test = np.array([[0,1,2,3],[1,0,1,2],[2,1,0,1],[4,2,1,0]])
    >>> lower = get_lower(test)
    >>> lower
    array([[1],
           [2],
           [1],
           [4],
           [2],
           [1]])

    """
    n = matrix.shape[0]
    lowvec = matrix[np.tril_indices(n, k=-1)].reshape(-1, 1)
    return lowvec


def fill_empty_diagonals(p):
    """
    Assign 1 to diagonal elements which fall in rows full of 0s to ensure
    the transition probability matrix is a stochastic one. Currently
    implemented for two- and three-dimensional transition probability
    matrices.

    Parameters
    ----------
    p        : array
               (k, k), an ergodic/non-ergodic Markov transition probability
               matrix.

    Returns
    -------
    p_temp   : array
               Matrix without rows full of 0 transition probabilities.
               (stochastic matrix)

    Examples
    --------
    >>> import numpy as np
    >>> from giddy.util import fill_empty_diagonals
    >>> p2 = np.array([[.5, .5, 0], [.3, .7, 0], [0, 0, 0]])
    >>> fill_empty_diagonals(p2)
    array([[0.5, 0.5, 0. ],
           [0.3, 0.7, 0. ],
           [0. , 0. , 1. ]])

    >>> p3 = np.array([[[0.5, 0.5, 0. ], [0.3, 0.7, 0. ], [0. , 0. , 0. ]],
    ...  [[0. , 0. , 0. ], [0.3, 0.7, 0. ], [0. , 0. , 0. ]]])
    >>> p_new = fill_empty_diagonals(p3)
    >>> p_new[1]
    array([[1. , 0. , 0. ],
           [0.3, 0.7, 0. ],
           [0. , 0. , 1. ]])
    """

    p_temp = np.asarray(p)
    if len(p_temp.shape) == 3:
        return _fill_empty_diagonal_3d(p_temp)
    elif len(p_temp.shape) == 2:
        return _fill_empty_diagonal_2d(p_temp)
    else:
        raise NotImplementedError(
            "Filling empty diagonals is " "only implemented for 2/3d matrices."
        )


def _fill_empty_diagonal_2d(p):
    """
    Assign 1 to diagonal elements which fall in rows full of 0s to ensure
    the transition probability matrix is a stochastic one.

    Parameters
    ----------
    p        : array
               (k, k), an ergodic/non-ergodic Markov transition probability
               matrix.

    Returns
    -------
    p_temp   : array
               Matrix without rows full of 0 transition probabilities.
               (stochastic matrix)

    """

    p_temp = copy.copy(p)
    p0 = p_temp.sum(axis=1) == 0
    if p0.sum() > 0:
        row_zero_i = np.where(p0)
        for row in row_zero_i:
            p_temp[row, row] = 1
    return p_temp


def _fill_empty_diagonal_3d(p):
    """
    Assign 1 to diagonal elements which fall in rows full of 0s to ensure
    the conditional transition probability matrices is are stochastic matrices.
    Staying probabilities are 1.

    Parameters
    ----------
    p        : array
               (m, k, k), m ergodic/non-ergodic Markov transition probability
               matrices.

    Returns
    -------
    p_temp   : array
               Matrices without rows full of 0 transition probabilities.
               (stochastic matrices)

    """

    p_temp = copy.copy(p)
    p0 = p_temp.sum(axis=2) == 0
    if p0.sum() > 0:
        rows, cols = np.where(p0)
        row_zero_i = list(zip(rows, cols))
        for row in row_zero_i:
            i, j = row
            p_temp[i, j, j] = 1
    return p_temp
