"""
Summary measures for ergodic Markov chains.
"""
__author__ = "Sergio J. Rey <sjsrey@gmail.com>, Wei Kang <weikang9009@gmail.com>"

__all__ = ["steady_state", "var_mfpt_ergodic", "mfpt"]

from warnings import warn

import numpy as np
import numpy.linalg as la
import quantecon as qe

from .util import fill_empty_diagonals


def _steady_state_ergodic(P):
    """
    Calculates the steady state probability vector for a regular Markov
    transition matrix P.

    Parameters
    ----------
    P        : array
               (k, k), an ergodic Markov transition probability matrix.

    Returns
    -------
             : array
               (k, ), steady state distribution.

    Examples
    --------
    Taken from :cite:`Kemeny1967`. Land of Oz example where the states are
    Rain, Nice and Snow, so there is 25 percent chance that if it
    rained in Oz today, it will snow tomorrow, while if it snowed today in
    Oz there is a 50 percent chance of snow again tomorrow and a 25
    percent chance of a nice day (nice, like when the witch with the monkeys
    is melting).

    >>> import numpy as np
    >>> import giddy
    >>> p=np.array([[.5, .25, .25],[.5,0,.5],[.25,.25,.5]])
    >>> giddy.ergodic._steady_state_ergodic(p)
    array([0.4, 0.2, 0.4])

    Thus, the long run distribution for Oz is to have 40 percent of the
    days classified as Rain, 20 percent as Nice, and 40 percent as Snow
    (states are mutually exclusive).

    """

    v, d = la.eig(np.transpose(P))
    d = np.array(d)

    # for a regular P maximum eigenvalue will be 1
    mv = max(v)
    # find its position
    i = v.tolist().index(mv)

    row = abs(d[:, i])

    # normalize eigenvector corresponding to the eigenvalue 1
    return row / sum(row)


def steady_state(P, fill_empty_classes=False):
    """
    Generalized function for calculating the steady state distribution
    for a regular or reducible Markov transition matrix P.

    Parameters
    ----------
    P        : array
               (k, k), an ergodic or non-ergodic Markov transition probability
               matrix.
    fill_empty_classes: bool, optional
                        If True, assign 1 to diagonal elements which fall in rows full
                        of 0s to ensure the transition probability matrix is a
                        stochastic one. Default is False.

    Returns
    -------
             : array
               If the Markov chain is irreducible, meaning that
               there is only one communicating class, there is one unique
               steady state distribution towards which the system is
               converging in the long run. Then steady_state is the
               same as _steady_state_ergodic (k, ).
               If the Markov chain is reducible, but only has 1 recurrent
               class, there will be one steady state distribution as well.
               If the Markov chain is reducible and there are multiple
               recurrent classes (num_rclasses), the system could be trapped
               in any one of  these recurrent classes. Then, there will be
               `num_rclasses` steady state distributions. The returned array
               will of (num_rclasses, k) dimension.

    Examples
    --------

    >>> import numpy as np
    >>> from giddy.ergodic import steady_state

    Irreducible Markov chain

    >>> p = np.array([[.5, .25, .25],[.5,0,.5],[.25,.25,.5]])
    >>> steady_state(p)
    array([0.4, 0.2, 0.4])

    Reducible Markov chain: two communicating classes

    >>> p = np.array([[.5, .5, 0],[.2,0.8,0],[0,0,1]])
    >>> steady_state(p)
    array([[0.28571429, 0.71428571, 0.        ],
           [0.        , 0.        , 1.        ]])

    Reducible Markov chain: two communicating classes

    >>> p = np.array([[.5, .5, 0],[.2,0.8,0],[0,0,0]])
    >>> steady_state(p, fill_empty_classes = True)
    array([[0.28571429, 0.71428571, 0.        ],
           [0.        , 0.        , 1.        ]])

    >>> steady_state(p, fill_empty_classes = False)
    Traceback (most recent call last):
        ...
    ValueError: Input transition probability matrix has 1 rows full of 0s. \
Please set fill_empty_classes=True to set diagonal elements for these \
rows to be 1 to make sure the matrix is stochastic.

    """

    P = np.asarray(P)
    rows0 = (P.sum(axis=1) == 0).sum()
    if rows0 > 0:
        if fill_empty_classes:
            P = fill_empty_diagonals(P)
        else:
            raise ValueError(
                "Input transition probability matrix has "
                "%d rows full of 0s. Please set "
                "fill_empty_classes=True to set diagonal "
                "elements for these rows to be 1 to make "
                "sure the matrix is stochastic." % rows0
            )
    mc = qe.MarkovChain(P)
    num_classes = mc.num_communication_classes
    if num_classes == 1:
        return mc.stationary_distributions[0]
    else:
        return mc.stationary_distributions


def _fmpt_ergodic(P):
    warn(
        "_fmpt_ergodic is deprecated. It will be replaced in giddy 2.5 with _mfpt_",
        DeprecationWarning,
        stacklevel=2,
    )
    return _mfpt_ergodic(P)


def _mfpt_ergodic(P):
    """
    Calculates the matrix of mean first passage times for an ergodic transition
    probability matrix.

    Parameters
    ----------
    P    : array
           (k, k), an ergodic Markov transition probability matrix.

    Returns
    -------
    M    : array
           (k, k), elements are the expected value for the number of intervals
           required for a chain starting in state i to first enter state j.
           If i=j then this is the recurrence time.

    Examples
    --------
    >>> import numpy as np
    >>> import giddy
    >>> p=np.array([[.5, .25, .25],[.5,0,.5],[.25,.25,.5]])
    >>> fm = giddy.ergodic._mfpt_ergodic(p)
    >>> fm
    array([[2.5       , 4.        , 3.33333333],
           [2.66666667, 5.        , 2.66666667],
           [3.33333333, 4.        , 2.5       ]])

    Thus, if it is raining today in Oz we can expect a nice day to come
    along in another 4 days, on average, and snow to hit in 3.33 days. We can
    expect another rainy day in 2.5 days. If it is nice today in Oz, we would
    experience a change in the weather (either rain or snow) in 2.67 days from
    today. (That wicked witch can only die once so I reckon that is the
    ultimate absorbing state).

    Notes
    -----
    Uses formulation (and examples on p. 218) in :cite:`Kemeny1967`.

    """

    P = np.asarray(P)
    k = P.shape[0]
    A = np.zeros_like(P)
    ss = _steady_state_ergodic(P)
    for j in range(k):
        A[:, j] = ss
    A = A.transpose()
    i = np.identity(k)
    Z = la.inv(i - P + A)
    E = np.ones_like(Z)
    A_diag = np.diag(A)
    A_diag = A_diag + (A_diag == 0)
    D = np.diag(1.0 / A_diag)
    Zdg = np.diag(np.diag(Z))
    M = (i - Z + E.dot(Zdg)).dot(D)
    return M


def fmpt(P, fill_empty_classes=False):
    warn(
        "fmpt is deprecated. It will be replaced in giddy 2.5 with mfpt",
        DeprecationWarning,
        stacklevel=2,
    )
    return mfpt(P, fill_empty_classes)


def mfpt(P, fill_empty_classes=False):
    """
    Generalized function for calculating mean first passage times for an
    ergodic or non-ergodic transition probability matrix.

    Parameters
    ----------
    P        : array
               (k, k), an ergodic/non-ergodic Markov transition probability
               matrix.
    fill_empty_classes: bool, optional
                        If True, assign 1 to diagonal elements which fall in rows full
                        of 0s to ensure the transition probability matrix is a
                        stochastic one. Default is False.

    Returns
    -------
    mfpt_all : array
               (k, k), elements are the expected value for the number of
               intervals required for a chain starting in state i to first
               enter state j. If i=j then this is the recurrence time.

    Examples
    --------
    >>> import numpy as np
    >>> from giddy.ergodic import mfpt
    >>> np.set_printoptions(suppress=True) #prevent scientific format

    Irreducible Markov chain

    >>> p = np.array([[.5, .25, .25],[.5,0,.5],[.25,.25,.5]])
    >>> fm = mfpt(p)
    >>> fm
    array([[2.5       , 4.        , 3.33333333],
           [2.66666667, 5.        , 2.66666667],
           [3.33333333, 4.        , 2.5       ]])

    Thus, if it is raining today in Oz we can expect a nice day to come
    along in another 4 days, on average, and snow to hit in 3.33 days. We can
    expect another rainy day in 2.5 days. If it is nice today in Oz, we would
    experience a change in the weather (either rain or snow) in 2.67 days from
    today.

    Reducible Markov chain: two communicating classes (this is an
    artificial example)

    >>> p = np.array([[.5, .5, 0],[.2,0.8,0],[0,0,1]])
    >>> mfpt(p)
    array([[3.5, 2. , inf],
           [5. , 1.4, inf],
           [inf, inf, 1. ]])

    Thus, if it is raining today in Oz we can expect a nice day to come
    along in another 2 days, on average, and should not expect snow to hit.
    We can expect another rainy day in 3.5 days. If it is nice today in Oz,
    we should expect a rainy day in 5 days.


    >>> p = np.array([[.5, .5, 0],[.2,0.8,0],[0,0,0]])
    >>> mfpt(p, fill_empty_classes=True)
    array([[3.5, 2. , inf],
           [5. , 1.4, inf],
           [inf, inf, 1. ]])

    >>> p = np.array([[.5, .5, 0],[.2,0.8,0],[0,0,0]])
    >>> mfpt(p, fill_empty_classes=False)
    Traceback (most recent call last):
        ...
    ValueError: Input transition probability matrix has 1 rows full of 0s. \
Please set fill_empty_classes=True to set diagonal elements for these \
rows to be 1 to make sure the matrix is stochastic.
    """

    P = np.asarray(P)
    rows0 = (P.sum(axis=1) == 0).sum()
    if rows0 > 0:
        if fill_empty_classes:
            P = fill_empty_diagonals(P)
        else:
            raise ValueError(
                "Input transition probability matrix has "
                "%d rows full of 0s. Please set "
                "fill_empty_classes=True to set diagonal "
                "elements for these rows to be 1 to make "
                "sure the matrix is stochastic." % rows0
            )
    mc = qe.MarkovChain(P)
    num_classes = mc.num_communication_classes
    if num_classes == 1:
        mfpt_all = _mfpt_ergodic(P)
    else:  # deal with non-ergodic Markov chains
        k = P.shape[0]
        mfpt_all = np.zeros((k, k))
        for desti in range(k):
            b = np.ones(k - 1)
            p_sub = np.delete(np.delete(P, desti, 0), desti, 1)
            p_calc = np.eye(k - 1) - p_sub
            m = np.full(k - 1, np.inf)
            row0 = (p_calc != 0).sum(axis=1)
            none0 = np.arange(k - 1)
            try:
                m[none0] = np.linalg.solve(p_calc, b)
            except np.linalg.LinAlgError as err:
                if "Singular matrix" in str(err) and (row0 == 0).sum() > 0:
                    index0 = set(np.argwhere(row0 == 0).flatten())
                    x = (p_calc[:, list(index0)] != 0).sum(axis=1)
                    setx = set(np.argwhere(x).flatten())
                    while not setx.issubset(index0):
                        index0 = index0.union(setx)
                        x = (p_calc[:, list(index0)] != 0).sum(axis=1)
                        setx = set(np.argwhere(x).flatten())
                    none0 = np.asarray(list(set(none0).difference(index0)))
                    if len(none0) >= 1:
                        p_calc = p_calc[none0, :][:, none0]
                        b = b[none0]
                        m[none0] = np.linalg.solve(p_calc, b)
            recc = (
                np.nan_to_num(
                    (np.delete(P, desti, 1)[desti] * m), 0, posinf=np.inf
                ).sum()
                + 1
            )
            mfpt_all[:, desti] = np.insert(m, desti, recc)
            mfpt_all = np.where(mfpt_all < -1e16, np.inf, mfpt_all)
            mfpt_all = np.where(mfpt_all > 1e16, np.inf, mfpt_all)
    return mfpt_all


def var_fmpt_ergodic(p):
    warn(
        (
            "var_fmpt_ergodic is deprecated. It will be "
            "replaced in giddy 2.5 with var_fmpt_ergodic"
        ),
        DeprecationWarning,
        stacklevel=2,
    )
    return var_mfpt_ergodic(p)


def var_mfpt_ergodic(p):
    """
    Variances of mean first passage times for an ergodic transition
    probability matrix.

    Parameters
    ----------
    P      : array
             (k, k), an ergodic Markov transition probability matrix.

    Returns
    -------
           : array
             (k, k), elements are the variances for the number of intervals
             required for a chain starting in state i to first enter state j.

    Examples
    --------
    >>> import numpy as np
    >>> from giddy.ergodic import var_mfpt_ergodic
    >>> p=np.array([[.5, .25, .25],[.5,0,.5],[.25,.25,.5]])
    >>> vfm=var_mfpt_ergodic(p)
    >>> vfm
    array([[ 5.58333333, 12.        ,  6.88888889],
           [ 6.22222222, 12.        ,  6.22222222],
           [ 6.88888889, 12.        ,  5.58333333]])

    Notes
    -----
    Uses formulation (and examples on p. 83) in :cite:`Kemeny1967`.


    """

    P = np.asarray(p)
    k = P.shape[0]
    A = _steady_state_ergodic(P)
    A = np.tile(A, (k, 1))
    i = np.identity(k)
    Z = la.inv(i - P + A)
    E = np.ones_like(Z)
    D = np.diag(1.0 / np.diag(A))
    Zdg = np.diag(np.diag(Z))
    M = (i - Z + E.dot(Zdg)).dot(D)
    ZM = Z.dot(M)
    ZMdg = np.diag(np.diag(ZM))
    W = M.dot(2 * Zdg.dot(D) - i) + 2 * (ZM - E.dot(ZMdg))
    return np.array(W - np.multiply(M, M))
