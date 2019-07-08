"""
Summary measures for ergodic Markov chains.
"""
__author__ = "Sergio J. Rey <sjsrey@gmail.com>, Wei Kang <weikang9009@gmail.com>"

__all__ = ['steady_state', 'fmpt', 'var_fmpt',
           'steady_state_general', 'fmpt_general']

import numpy as np
import numpy.linalg as la
import quantecon as qe
from .util import fill_diag3, fill_diag2


def steady_state(P):
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
    >>> from giddy.ergodic import steady_state
    >>> p=np.array([[.5, .25, .25],[.5,0,.5],[.25,.25,.5]])
    >>> steady_state(p)
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

def steady_state_general(P, fill_diag=True):
    """
    Generalized function for calculating the steady state distribution
    for a regular or reducible Markov transition matrix P.

    Parameters
    ----------
    P        : array
               (k, k), an ergodic or non-ergodic Markov transition probability
               matrix.
    fill_diag: bool
               If True, assign 0 to diagonal elements which fall in rows full
               of 0s to ensure the transition probability matrix is a
               stochastic one.

    Returns
    -------
             : array
               If the Markov chain is irreducible, meaning that
               there is only one communicating class, there is one unique
               steady state distribution towards which the system is
               converging in the long run. Then steady_state_general is the
               same as steady_state (k, ).
               If the Markov chain is reducible, meaning that there are
               more than one communicating class (e.g. `num_classes` = 3),
               the system could be trapped in any one of these communicating
               classes. Then, there will be `num_classes` steady state
               distributions. The returned array will of (num_classes,
               k) dimension.

    Examples
    --------

    >>> import numpy as np
    >>> from giddy.ergodic import steady_state_general

    # irreducible Markov chain
    >>> p = np.array([[.5, .25, .25],[.5,0,.5],[.25,.25,.5]])
    >>> steady_state_general(p)
    array([0.4, 0.2, 0.4])

    # reducible Markov chain: two communicating classes
    >>> p = np.array([[.5, .5, 0],[.2,0.8,0],[0,0,1]])
    >>> steady_state_general(p)
    array([[0.28571429, 0.71428571, 0.        ],
           [0.        , 0.        , 1.        ]])

    # reducible Markov chain: two communicating classes
    >>> p = np.array([[.5, .5, 0],[.2,0.8,0],[0,0,0]])
    >>> steady_state_general(p, fill_diag =True)
    array([[0.28571429, 0.71428571, 0.        ],
           [0.        , 0.        , 1.        ]])
    """

    P = np.asarray(P)
    if fill_diag:
        if (P.sum(axis=1) == 0).sum() > 0:
            P = fill_diag2(P)
    mc = qe.MarkovChain(P)
    num_classes = mc.num_communication_classes
    if num_classes == 1:
        return mc.stationary_distributions[0]
    else:
        return mc.stationary_distributions

def fmpt(P):
    """
    Calculates the matrix of first mean passage times for an ergodic transition
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
    >>> from giddy.ergodic import fmpt
    >>> p=np.array([[.5, .25, .25],[.5,0,.5],[.25,.25,.5]])
    >>> fm=fmpt(p)
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

    P = np.matrix(P)
    k = P.shape[0]
    A = np.zeros_like(P)
    ss = steady_state(P).reshape(k, 1)
    for i in range(k):
        A[:, i] = ss
    A = A.transpose()
    I = np.identity(k)
    Z = la.inv(I - P + A)
    E = np.ones_like(Z)
    A_diag = np.diag(A)
    A_diag = A_diag + (A_diag == 0)
    D = np.diag(1. / A_diag)
    Zdg = np.diag(np.diag(Z))
    M = (I - Z + E * Zdg) * D
    return np.array(M)

def fmpt_general(P, fill_diag=False):
    """
    Generalized function for calculating first mean passage times for an
    ergodic or non-ergodic transition probability matrix.

    Parameters
    ----------
    P        : array
               (k, k), an ergodic/non-ergodic Markov transition probability
               matrix.
    fill_diag: bool
               If True, assign 0 to diagonal elements which fall in rows full
               of 0s to ensure the transition probability matrix is a
               stochastic one.

    Returns
    -------
    fmpt_all : array
               (k, k), elements are the expected value for the number of
               intervals required for a chain starting in state i to first
               enter state j. If i=j then this is the recurrence time.

    Examples
    --------
    >>> import numpy as np
    >>> from giddy.ergodic import fmpt_general

    # irreducible Markov chain
    >>> p = np.array([[.5, .25, .25],[.5,0,.5],[.25,.25,.5]])
    >>> fm = fmpt_general(p)
    >>> fm
    array([[2.5       , 4.        , 3.33333333],
           [2.66666667, 5.        , 2.66666667],
           [3.33333333, 4.        , 2.5       ]])

    Thus, if it is raining today in Oz we can expect a nice day to come
    along in another 4 days, on average, and snow to hit in 3.33 days. We can
    expect another rainy day in 2.5 days. If it is nice today in Oz, we would
    experience a change in the weather (either rain or snow) in 2.67 days from
    today.

    # reducible Markov chain: two communicating classes (this is an
    artificial example)
    >>> p = np.array([[.5, .5, 0],[.2,0.8,0],[0,0,1]])
    >>> fmpt_general(p)
    array([[3.5, 2. , inf],
           [5. , 1.4, inf],
           [inf, inf, 1. ]])

    Thus, if it is raining today in Oz we can expect a nice day to come
    along in another 2 days, on average, and should not expect snow to hit.
    We can expect another rainy day in 3.5 days. If it is nice today in Oz,
    we should expect a rainy day in 5 days.


    >>> p = np.array([[.5, .5, 0],[.2,0.8,0],[0,0,0]])
    >>> fmpt_general(p, fill_diag=True)
    array([[3.5, 2. , inf],
           [5. , 1.4, inf],
           [inf, inf, 1. ]])

    """

    P = np.asarray(P)
    if fill_diag:
        if (P.sum(axis=1) == 0).sum() > 0:
            P = fill_diag2(P)
    mc = qe.MarkovChain(P)
    num_classes = mc.num_communication_classes
    if num_classes == 1:
        fmpt_all = fmpt(P)
        return fmpt_all
    else:
        i_cclasses = mc.communication_classes_indices
        fmpt_all = np.full((mc.n, mc.n), np.inf)
        for cclass in i_cclasses:
            rows = cclass[:, np.newaxis]
            p_temp = P[rows, cclass]
            fmpt_all[rows, cclass] = fmpt(p_temp)
        return fmpt_all



def var_fmpt(P):
    """
    Variances of first mean passage times for an ergodic transition
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
    >>> from giddy.ergodic import var_fmpt
    >>> p=np.array([[.5, .25, .25],[.5,0,.5],[.25,.25,.5]])
    >>> vfm=var_fmpt(p)
    >>> vfm
    array([[ 5.58333333, 12.        ,  6.88888889],
           [ 6.22222222, 12.        ,  6.22222222],
           [ 6.88888889, 12.        ,  5.58333333]])

    Notes
    -----
    Uses formulation (and examples on p. 83) in :cite:`Kemeny1967`.


    """

    P = np.matrix(P)
    A = P ** 1000
    n, k = A.shape
    I = np.identity(k)
    Z = la.inv(I - P + A)
    E = np.ones_like(Z)
    D = np.diag(1. / np.diag(A))
    Zdg = np.diag(np.diag(Z))
    M = (I - Z + E * Zdg) * D
    ZM = Z * M
    ZMdg = np.diag(np.diag(ZM))
    W = M * (2 * Zdg * D - I) + 2 * (ZM - E * ZMdg)
    return np.array(W - np.multiply(M, M))
