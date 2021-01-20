"""
Markov based methods for spatial dynamics.
"""
__author__ = "Sergio J. Rey <sjsrey@gmail.com>, Wei Kang <weikang9009@gmail.com>"

__all__ = [
    "Markov",
    "LISA_Markov",
    "Spatial_Markov",
    "kullback",
    "prais",
    "homogeneity",
    "FullRank_Markov",
    "sojourn_time",
    "GeoRank_Markov",
]

import numpy as np
from .ergodic import steady_state, fmpt
from .util import fill_empty_diagonals
from .components import Graph
from scipy import stats
from scipy.stats import rankdata
from operator import gt
from libpysal import weights
from esda.moran import Moran_Local
import mapclassify as mc
import itertools
import quantecon as qe

# TT predefine LISA transitions
# TT[i,j] is the transition type from i to j
# i = quadrant in period 0
# j = quadrant in period 1
# uses one offset so first row and col of TT are ignored
TT = np.zeros((5, 5), int)
c = 1
for i in range(1, 5):
    for j in range(1, 5):
        TT[i, j] = c
        c += 1

# MOVE_TYPES is a dictionary that returns the move type of a LISA transition
# filtered on the significance of the LISA end points
# True indicates significant LISA in a particular period
# e.g. a key of (1, 3, True, False) indicates a significant LISA located in
# quadrant 1 in period 0 moved to quadrant 3 in period 1 but was not
# significant in quadrant 3.

MOVE_TYPES = {}
c = 1
cases = (True, False)
sig_keys = [(i, j) for i in cases for j in cases]

for i, sig_key in enumerate(sig_keys):
    c = 1 + i * 16
    for i in range(1, 5):
        for j in range(1, 5):
            key = (i, j, sig_key[0], sig_key[1])
            MOVE_TYPES[key] = c
            c += 1


class Markov(object):
    """
    Classic Markov Chain estimation.

    Parameters
    ----------
    class_ids    : array
                   (n, t), one row per observation, one column recording the
                   state of each observation, with as many columns as time
                   periods.
    classes      : array
                   (k, 1), all different classes (bins) of the matrix.
    fill_empty_classes: bool
                        If True, assign 1 to diagonal elements which fall in rows
                        full of 0s to ensure p is a stochastic transition
                        probability matrix (each row sums up to 1).
    summary      : bool
                   If True, print out the summary of the Markov Chain during
                   initialization. Default is True.

    Attributes
    ----------
    k            : int
                   Number of Markov states.
    p            : array
                   (k, k), transition probability matrix.
    num_cclasses : int
                   Number of communicating classes.
    cclasses_indices : list
                       List of indices within each communicating classes.
    num_rclasses : int
                   Number of recurrent classes.
    rclasses_indices : list
                       List of indices within each recurrent classes.
    num_astates  : int
                   Number of absorbing states.
    astates_indices  : list
                       List of indices of absorbing states.
    steady_state : array
                   Steady state distributions. If the Markov chain only has
                   one recurrent class (num_rclasses=1), it will converge to
                   an unique distribution in the long run, and thus steady_state
                   is of (k, ) dimension; if the Markov chain has multiple
                   recurrent classes (num_rclasses>1), there will be
                   (num_rclasses) steady state distributions and steady_state
                   will be of (num_rclasses, k) dimension.
    transitions  : array
                   (k, k), count of transitions between each state i and j.

    Examples
    --------
    >>> import numpy as np
    >>> from giddy.markov import Markov
    >>> c = [['b','a','c'],['c','c','a'],['c','b','c']]
    >>> c.extend([['a','a','b'], ['a','b','c']])
    >>> c = np.array(c)
    >>> m = Markov(c)
    The Markov Chain is irreducible and is composed by:
    1 Recurrent class (indices):
    [0 1 2]
    0 Transient classes.
    The Markov Chain has 0 absorbing states.
    >>> m.classes.tolist()
    ['a', 'b', 'c']
    >>> m.p
    array([[0.25      , 0.5       , 0.25      ],
           [0.33333333, 0.        , 0.66666667],
           [0.33333333, 0.33333333, 0.33333333]])
    >>> m.steady_state
    array([0.30769231, 0.28846154, 0.40384615])

    Reducible Markov chain

    >>> c = [['b','a','a'],['c','c','a'],['c','b','c']]
    >>> m = Markov(c)
    The Markov Chain is reducible and is composed by:
    1 Recurrent class (indices):
    [0]
    1 Transient class (indices):
    [1 2]
    The Markov Chain has 1 absorbing state (index):
    [0]

    US nominal per capita income 48 states 81 years 1929-2009

    >>> import libpysal
    >>> import mapclassify as mc
    >>> f = libpysal.io.open(libpysal.examples.get_path("usjoin.csv"))
    >>> pci = np.array([f.by_col[str(y)] for y in range(1929,2010)])

    set classes to quintiles for each year

    >>> q5 = np.array([mc.Quantiles(y).yb for y in pci]).transpose()
    >>> m = Markov(q5)
    The Markov Chain is irreducible and is composed by:
    1 Recurrent class (indices):
    [0 1 2 3 4]
    0 Transient classes.
    The Markov Chain has 0 absorbing states.
    >>> m.transitions
    array([[729.,  71.,   1.,   0.,   0.],
           [ 72., 567.,  80.,   3.,   0.],
           [  0.,  81., 631.,  86.,   2.],
           [  0.,   3.,  86., 573.,  56.],
           [  0.,   0.,   1.,  57., 741.]])
    >>> m.p
    array([[0.91011236, 0.0886392 , 0.00124844, 0.        , 0.        ],
           [0.09972299, 0.78531856, 0.11080332, 0.00415512, 0.        ],
           [0.        , 0.10125   , 0.78875   , 0.1075    , 0.0025    ],
           [0.        , 0.00417827, 0.11977716, 0.79805014, 0.07799443],
           [0.        , 0.        , 0.00125156, 0.07133917, 0.92740926]])
    >>> m.steady_state
    array([0.20774716, 0.18725774, 0.20740537, 0.18821787, 0.20937187])

    Relative incomes

    >>> pci = pci.transpose()
    >>> rpci = pci/(pci.mean(axis=0))
    >>> rq = mc.Quantiles(rpci.flatten()).yb.reshape(pci.shape)
    >>> mq = Markov(rq)
    The Markov Chain is irreducible and is composed by:
    1 Recurrent class (indices):
    [0 1 2 3 4]
    0 Transient classes.
    The Markov Chain has 0 absorbing states.
    >>> mq.transitions
    array([[707.,  58.,   7.,   1.,   0.],
           [ 50., 629.,  80.,   1.,   1.],
           [  4.,  79., 610.,  73.,   2.],
           [  0.,   7.,  72., 650.,  37.],
           [  0.,   0.,   0.,  48., 724.]])
    >>> mq.steady_state
    array([0.17957376, 0.21631443, 0.21499942, 0.21134662, 0.17776576])

    """

    def __init__(self, class_ids, classes=None, fill_empty_classes=False, summary=True):
        if classes is not None:
            self.classes = classes
        else:
            self.classes = np.unique(class_ids)

        class_ids = np.array(class_ids)
        n, t = class_ids.shape
        k = len(self.classes)
        self.k = k
        js = list(range(t - 1))

        classIds = self.classes.tolist()
        transitions = np.zeros((k, k))
        for state_0 in js:
            state_1 = state_0 + 1
            state_0 = class_ids[:, state_0]
            state_1 = class_ids[:, state_1]
            initial = np.unique(state_0)
            for i in initial:
                ending = state_1[state_0 == i]
                uending = np.unique(ending)
                row = classIds.index(i)
                for j in uending:
                    col = classIds.index(j)
                    transitions[row, col] += sum(ending == j)
        self.transitions = transitions
        row_sum = transitions.sum(axis=1)
        self.p = np.dot(np.diag(1 / (row_sum + (row_sum == 0))), transitions)

        if fill_empty_classes:
            self.p = fill_empty_diagonals(self.p)

        p_temp = self.p
        if (p_temp.sum(axis=1) == 0).sum() > 0:
            p_temp = fill_empty_diagonals(p_temp)
        markovchain = qe.MarkovChain(p_temp)
        self.num_cclasses = markovchain.num_communication_classes
        self.num_rclasses = markovchain.num_recurrent_classes

        self.cclasses_indices = markovchain.communication_classes_indices
        self.rclasses_indices = markovchain.recurrent_classes_indices
        transient = set(list(map(tuple, self.cclasses_indices))).difference(
            set(list(map(tuple, self.rclasses_indices)))
        )
        self.num_tclasses = len(transient)
        if len(transient):
            self.tclasses_indices = [np.asarray(i) for i in transient]
        else:
            self.tclasses_indices = None
        self.astates_indices = list(np.argwhere(np.diag(p_temp) == 1))
        self.num_astates = len(self.astates_indices)

        if summary:
            if markovchain.is_irreducible:
                print("The Markov Chain is irreducible and is composed by:")
            else:
                print("The Markov Chain is reducible and is composed by:")
            if self.num_rclasses == 1:
                print("1 Recurrent class (indices):")
            else:
                print("{0} Recurrent classes (indices):".format(self.num_rclasses))
            print(*self.rclasses_indices, sep=", ")
            if self.num_tclasses == 0:
                print("0 Transient classes.")
            else:
                if self.num_tclasses == 1:
                    print("1 Transient class (indices):")
                else:
                    print("{0} Transient classes (indices):".format(self.num_tclasses))
                print(*self.tclasses_indices, sep=", ")
            if self.num_astates == 0:
                print("The Markov Chain has 0 absorbing states.")
            else:
                if self.num_astates == 1:
                    print("The Markov Chain has 1 absorbing state (index):")
                else:
                    print(
                        "The Markov Chain has {0} absorbing states (indices):".format(
                            self.num_astates
                        )
                    )
                print(*self.astates_indices, sep=", ")

    @property
    def fmpt(self):
        if not hasattr(self, "_fmpt"):
            self._fmpt = fmpt(self.p, fill_empty_classes=True)
        return self._fmpt

    @property
    def steady_state(self):
        if not hasattr(self, "_steady_state"):
            self._steady_state = steady_state(self.p, fill_empty_classes=True)
        return self._steady_state

    @property
    def sojourn_time(self):
        if not hasattr(self, "_st"):
            self._st = sojourn_time(self.p)
        return self._st


class Spatial_Markov(object):
    """
    Markov transitions conditioned on the value of the spatial lag.

    Parameters
    ----------
    y               : array
                      (n, t), one row per observation, one column per state of
                      each observation, with as many columns as time periods.
    w               : W
                      spatial weights object.
    k               : integer, optional
                      number of classes (quantiles) for input time series y.
                      Default is 4. If discrete=True, k is determined
                      endogenously.
    m               : integer, optional
                      number of classes (quantiles) for the spatial lags of
                      regional time series. Default is 4. If discrete=True,
                      m is determined endogenously.
    permutations    : int, optional
                      number of permutations for use in randomization based
                      inference (the default is 0).
    fixed           : bool, optional
                      If true, discretization are taken over the entire n*t
                      pooled series and cutoffs can be user-defined. If
                      cutoffs and lag_cutoffs are not given, quantiles are
                      used. If false, quantiles are taken each time period
                      over n. Default is True.
    discrete        : bool, optional
                      If true, categorical spatial lags which are most common
                      categories of neighboring observations serve as the
                      conditioning and fixed is ignored; if false, weighted
                      averages of neighboring observations are used. Default is
                      false.
    cutoffs         : array, optional
                      users can specify the discretization cutoffs for
                      continuous time series. Default is None, meaning that
                      quantiles will be used for the discretization.
    lag_cutoffs     : array, optional
                      users can specify the discretization cutoffs for the
                      spatial lags of continuous time series. Default is
                      None, meaning that quantiles will be used for the
                      discretization.
    variable_name   : string
                      name of variable.
    fill_empty_classes: bool
                        If True, assign 1 to diagonal elements which fall in rows
                        full of 0s to ensure each conditional transition
                        probability matrix is a stochastic matrix (each row
                        sums up to 1). In other words, the probability of
                        staying at that state is 1.

    Attributes
    ----------
    class_ids       : array
                      (n, t), discretized series if y is continuous. Otherwise
                      it is identical to y.
    classes         : array
                      (k, 1), all different classes (bins).
    lclass_ids      : array
                      (n, t), spatial lag series.
    lclasses        : array
                      (k, 1), all different classes (bins) for
                      spatial lags.
    p               : array
                      (k, k), transition probability matrix for a-spatial
                      Markov.
    s               : array
                      (k, ), steady state distribution for a-spatial Markov.
    f               : array
                      (k, k), first mean passage times for a-spatial Markov.
    transitions     : array
                      (k, k), counts of transitions between each state i and j
                      for a-spatial Markov.
    T               : array
                      (m, k, k), counts of transitions for each conditional
                      Markov.  T[0] is the matrix of transitions for
                      observations with lags in the 0th quantile; T[m-1] is the
                      transitions for the observations with lags in the m-1th.
    P               : array
                      (m, k, k), transition probability matrix for spatial
                      Markov first dimension is the conditioned on the lag.
    S               : arraylike
                      (m, k), steady state distributions for spatial Markov.
                      Each row is a conditional steady state distribution.
                      If one (or more) spatially conditional Markov chain is
                      reducible (having more than 1 steady state distribution),
                      this attribute is an array of m arrays of varying
                      dimensions.
    F               : array
                      (m, k, k),first mean passage times.
                      First dimension is conditioned on the spatial lag.
    shtest          : list
                      (k elements), each element of the list is a tuple for a
                      multinomial difference test between the steady state
                      distribution from a conditional distribution versus the
                      overall steady state distribution: first element of the
                      tuple is the chi2 value, second its p-value and the third
                      the degrees of freedom.
    chi2            : list
                      (k elements), each element of the list is a tuple for a
                      chi-squared test of the difference between the
                      conditional transition matrix against the overall
                      transition matrix: first element of the tuple is the chi2
                      value, second its p-value and the third the degrees of
                      freedom.
    x2              : float
                      sum of the chi2 values for each of the conditional tests.
                      Has an asymptotic chi2 distribution with k(k-1)(k-1)
                      degrees of freedom. Under the null that transition
                      probabilities are spatially homogeneous.
                      (see chi2 above)
    x2_dof          : int
                      degrees of freedom for homogeneity test.
    x2_pvalue       : float
                      pvalue for homogeneity test based on analytic.
                      distribution
    x2_rpvalue      : float
                      (if permutations>0)
                      pseudo p-value for x2 based on random spatial
                      permutations of the rows of the original transitions.
    x2_realizations : array
                      (permutations,1), the values of x2 for the random
                      permutations.
    Q               : float
                      Chi-square test of homogeneity across lag classes based
                      on :cite:`Bickenbach2003`.
    Q_p_value       : float
                      p-value for Q.
    LR              : float
                      Likelihood ratio statistic for homogeneity across lag
                      classes based on :cite:`Bickenbach2003`.
    LR_p_value      : float
                      p-value for LR.
    dof_hom         : int
                      degrees of freedom for LR and Q, corrected for 0 cells.

    Notes
    -----
    Based on :cite:`Rey2001`.

    The shtest and chi2 tests should be used with caution as they are based on
    classic theory assuming random transitions. The x2 based test is
    preferable since it simulates the randomness under the null. It is an
    experimental test requiring further analysis.

    Examples
    --------
    >>> import libpysal
    >>> from giddy.markov import Spatial_Markov
    >>> import numpy as np
    >>> f = libpysal.io.open(libpysal.examples.get_path("usjoin.csv"))
    >>> pci = np.array([f.by_col[str(y)] for y in range(1929,2010)])
    >>> pci = pci.transpose()
    >>> rpci = pci/(pci.mean(axis=0))
    >>> w = libpysal.io.open(libpysal.examples.get_path("states48.gal")).read()
    >>> w.transform = 'r'

    Now we create a `Spatial_Markov` instance for the continuous relative per
    capita income time series for 48 US lower states 1929-2009. The current
    implementation allows users to classify the continuous incomes in a more
    flexible way.

    (1) Global quintiles to discretize the income data (k=5), and global
    quintiles to discretize the spatial lags of incomes (m=5).

    >>> sm = Spatial_Markov(rpci, w, fixed=True, k=5, m=5, variable_name='rpci')

    We can examine the cutoffs for the incomes and cutoffs for the spatial lags

    >>> sm.cutoffs
    array([0.83999133, 0.94707545, 1.03242697, 1.14911154])
    >>> sm.lag_cutoffs
    array([0.88973386, 0.95891917, 1.01469758, 1.1183566 ])

    Obviously, they are slightly different.

    We now look at the estimated spatially lag conditioned transition
    probability matrices.

    >>> for p in sm.P:
    ...     print(p)
    [[0.96341463 0.0304878  0.00609756 0.         0.        ]
     [0.06040268 0.83221477 0.10738255 0.         0.        ]
     [0.         0.14       0.74       0.12       0.        ]
     [0.         0.03571429 0.32142857 0.57142857 0.07142857]
     [0.         0.         0.         0.16666667 0.83333333]]
    [[0.79831933 0.16806723 0.03361345 0.         0.        ]
     [0.0754717  0.88207547 0.04245283 0.         0.        ]
     [0.00537634 0.06989247 0.8655914  0.05913978 0.        ]
     [0.         0.         0.06372549 0.90196078 0.03431373]
     [0.         0.         0.         0.19444444 0.80555556]]
    [[0.84693878 0.15306122 0.         0.         0.        ]
     [0.08133971 0.78947368 0.1291866  0.         0.        ]
     [0.00518135 0.0984456  0.79274611 0.0984456  0.00518135]
     [0.         0.         0.09411765 0.87058824 0.03529412]
     [0.         0.         0.         0.10204082 0.89795918]]
    [[0.8852459  0.09836066 0.         0.01639344 0.        ]
     [0.03875969 0.81395349 0.13953488 0.         0.00775194]
     [0.0049505  0.09405941 0.77722772 0.11881188 0.0049505 ]
     [0.         0.02339181 0.12865497 0.75438596 0.09356725]
     [0.         0.         0.         0.09661836 0.90338164]]
    [[0.33333333 0.66666667 0.         0.         0.        ]
     [0.0483871  0.77419355 0.16129032 0.01612903 0.        ]
     [0.01149425 0.16091954 0.74712644 0.08045977 0.        ]
     [0.         0.01036269 0.06217617 0.89637306 0.03108808]
     [0.         0.         0.         0.02352941 0.97647059]]


    The probability of a poor state remaining poor is 0.963 if their
    neighbors are in the 1st quintile and 0.798 if their neighbors are
    in the 2nd quintile. The probability of a rich economy remaining
    rich is 0.976 if their neighbors are in the 5th quintile, but if their
    neighbors are in the 4th quintile this drops to 0.903.

    The global transition probability matrix is estimated:

    >>> print(sm.p)
    [[0.91461837 0.07503234 0.00905563 0.00129366 0.        ]
     [0.06570302 0.82654402 0.10512484 0.00131406 0.00131406]
     [0.00520833 0.10286458 0.79427083 0.09505208 0.00260417]
     [0.         0.00913838 0.09399478 0.84856397 0.04830287]
     [0.         0.         0.         0.06217617 0.93782383]]

    The Q and likelihood ratio statistics are both significant indicating
    the dynamics are not homogeneous across the lag classes:

    >>> "%.3f"%sm.LR
    '170.659'
    >>> "%.3f"%sm.Q
    '200.624'
    >>> "%.3f"%sm.LR_p_value
    '0.000'
    >>> "%.3f"%sm.Q_p_value
    '0.000'
    >>> sm.dof_hom
    60

    The long run distribution for states with poor (rich) neighbors has
    0.435 (0.018) of the values in the first quintile, 0.263 (0.200) in
    the second quintile, 0.204 (0.190) in the third, 0.0684 (0.255) in the
    fourth and 0.029 (0.337) in the fifth quintile.

    >>> sm.S
    array([[0.43509425, 0.2635327 , 0.20363044, 0.06841983, 0.02932278],
           [0.13391287, 0.33993305, 0.25153036, 0.23343016, 0.04119356],
           [0.12124869, 0.21137444, 0.2635101 , 0.29013417, 0.1137326 ],
           [0.0776413 , 0.19748806, 0.25352636, 0.22480415, 0.24654013],
           [0.01776781, 0.19964349, 0.19009833, 0.25524697, 0.3372434 ]])

    States with incomes in the first quintile with neighbors in the
    first quintile return to the first quartile after 2.298 years, after
    leaving the first quintile. They enter the fourth quintile after
    80.810 years after leaving the first quintile, on average.
    Poor states within neighbors in the fourth quintile return to the
    first quintile, on average, after 12.88 years, and would enter the
    fourth quintile after 28.473 years.

    >>> for f in sm.F:
    ...     print(f)
    [[  2.29835259  28.95614035  46.14285714  80.80952381 279.42857143]
     [ 33.86549708   3.79459555  22.57142857  57.23809524 255.85714286]
     [ 43.60233918   9.73684211   4.91085714  34.66666667 233.28571429]
     [ 46.62865497  12.76315789   6.25714286  14.61564626 198.61904762]
     [ 52.62865497  18.76315789  12.25714286   6.          34.1031746 ]]
    [[  7.46754205   9.70574606  25.76785714  74.53116883 194.23446197]
     [ 27.76691978   2.94175577  24.97142857  73.73474026 193.4380334 ]
     [ 53.57477715  28.48447637   3.97566318  48.76331169 168.46660482]
     [ 72.03631562  46.94601483  18.46153846   4.28393653 119.70329314]
     [ 77.17917276  52.08887197  23.6043956    5.14285714  24.27564033]]
    [[  8.24751154   6.53333333  18.38765432  40.70864198 112.76732026]
     [ 47.35040872   4.73094099  11.85432099  34.17530864 106.23398693]
     [ 69.42288828  24.76666667   3.794921    22.32098765  94.37966594]
     [ 83.72288828  39.06666667  14.3          3.44668119  76.36702977]
     [ 93.52288828  48.86666667  24.1          9.8          8.79255406]]
    [[ 12.87974382  13.34847151  19.83446328  28.47257282  55.82395142]
     [ 99.46114206   5.06359731  10.54545198  23.05133495  49.68944423]
     [117.76777159  23.03735526   3.94436301  15.0843986   43.57927247]
     [127.89752089  32.4393006   14.56853107   4.44831643  31.63099455]
     [138.24752089  42.7893006   24.91853107  10.35         4.05613474]]
    [[ 56.2815534    1.5         10.57236842  27.02173913 110.54347826]
     [ 82.9223301    5.00892857   9.07236842  25.52173913 109.04347826]
     [ 97.17718447  19.53125      5.26043557  21.42391304 104.94565217]
     [127.1407767   48.74107143  33.29605263   3.91777427  83.52173913]
     [169.6407767   91.24107143  75.79605263  42.5          2.96521739]]

    (2) Global quintiles to discretize the income data (k=5), and global
    quartiles to discretize the spatial lags of incomes (m=4).

    >>> sm = Spatial_Markov(rpci, w, fixed=True, k=5, m=4, variable_name='rpci')

    We can also examine the cutoffs for the incomes and cutoffs for the spatial
    lags:

    >>> sm.cutoffs
    array([0.83999133, 0.94707545, 1.03242697, 1.14911154])
    >>> sm.lag_cutoffs
    array([0.91440247, 0.98583079, 1.08698351])

    We now look at the estimated spatially lag conditioned transition
    probability matrices.

    >>> for p in sm.P:
    ...     print(p)
    [[0.95708955 0.03544776 0.00746269 0.         0.        ]
     [0.05825243 0.83980583 0.10194175 0.         0.        ]
     [0.         0.1294964  0.76258993 0.10791367 0.        ]
     [0.         0.01538462 0.18461538 0.72307692 0.07692308]
     [0.         0.         0.         0.14285714 0.85714286]]
    [[0.7421875  0.234375   0.0234375  0.         0.        ]
     [0.08550186 0.85130112 0.06319703 0.         0.        ]
     [0.00865801 0.06926407 0.86147186 0.05627706 0.004329  ]
     [0.         0.         0.05363985 0.92337165 0.02298851]
     [0.         0.         0.         0.13432836 0.86567164]]
    [[0.95145631 0.04854369 0.         0.         0.        ]
     [0.06       0.79       0.145      0.         0.005     ]
     [0.00358423 0.10394265 0.7921147  0.09677419 0.00358423]
     [0.         0.01630435 0.13586957 0.75543478 0.0923913 ]
     [0.         0.         0.         0.10204082 0.89795918]]
    [[0.16666667 0.66666667 0.         0.16666667 0.        ]
     [0.03488372 0.80232558 0.15116279 0.01162791 0.        ]
     [0.00840336 0.13445378 0.70588235 0.1512605  0.        ]
     [0.         0.01171875 0.08203125 0.87109375 0.03515625]
     [0.         0.         0.         0.03434343 0.96565657]]

    We now obtain 4 5*5 spatial lag conditioned transition probability
    matrices instead of 5 as in case (1).

    The Q and likelihood ratio statistics are still both significant.

    >>> "%.3f"%sm.LR
    '172.105'
    >>> "%.3f"%sm.Q
    '321.128'
    >>> "%.3f"%sm.LR_p_value
    '0.000'
    >>> "%.3f"%sm.Q_p_value
    '0.000'
    >>> sm.dof_hom
    45

    (3) We can also set the cutoffs for relative incomes and their
    spatial lags manually.
    For example, we want the defining cutoffs to be [0.8, 0.9, 1, 1.2],
    meaning that relative incomes:
    2.1 smaller than 0.8 : class 0
    2.2 between 0.8 and 0.9: class 1
    2.3 between 0.9 and 1.0 : class 2
    2.4 between 1.0 and 1.2: class 3
    2.5 larger than 1.2: class 4

    >>> cc = np.array([0.8, 0.9, 1, 1.2])
    >>> sm = Spatial_Markov(rpci, w, cutoffs=cc, lag_cutoffs=cc, variable_name='rpci')
    >>> sm.cutoffs
    array([0.8, 0.9, 1. , 1.2])
    >>> sm.k
    5
    >>> sm.lag_cutoffs
    array([0.8, 0.9, 1. , 1.2])
    >>> sm.m
    5
    >>> for p in sm.P:
    ...     print(p)
    [[0.96703297 0.03296703 0.         0.         0.        ]
     [0.10638298 0.68085106 0.21276596 0.         0.        ]
     [0.         0.14285714 0.7755102  0.08163265 0.        ]
     [0.         0.         0.5        0.5        0.        ]
     [0.         0.         0.         0.         0.        ]]
    [[0.88636364 0.10606061 0.00757576 0.         0.        ]
     [0.04402516 0.89308176 0.06289308 0.         0.        ]
     [0.         0.05882353 0.8627451  0.07843137 0.        ]
     [0.         0.         0.13846154 0.86153846 0.        ]
     [0.         0.         0.         0.         1.        ]]
    [[0.78082192 0.17808219 0.02739726 0.01369863 0.        ]
     [0.03488372 0.90406977 0.05813953 0.00290698 0.        ]
     [0.         0.05919003 0.84735202 0.09034268 0.00311526]
     [0.         0.         0.05811623 0.92985972 0.01202405]
     [0.         0.         0.         0.14285714 0.85714286]]
    [[0.82692308 0.15384615 0.         0.01923077 0.        ]
     [0.0703125  0.7890625  0.125      0.015625   0.        ]
     [0.00295858 0.06213018 0.82248521 0.10946746 0.00295858]
     [0.         0.00185529 0.07606679 0.88497217 0.03710575]
     [0.         0.         0.         0.07803468 0.92196532]]
    [[0.         0.         0.         0.         0.        ]
     [0.         0.         0.         0.         0.        ]
     [0.         0.06666667 0.9        0.03333333 0.        ]
     [0.         0.         0.05660377 0.90566038 0.03773585]
     [0.         0.         0.         0.03932584 0.96067416]]

    (3.1) As we can see from the above estimated conditional transition
    probability matrix, some rows are full of zeros which violate the
    requirement of a transition probability matrix that every row sums to 1.
    We can easily adjust this assigning fill_empty_classes = True when initializing
    Spatial_Markov.

    >>> sm = Spatial_Markov(rpci, w, cutoffs=cc, lag_cutoffs=cc, fill_empty_classes=True)
    >>> for p in sm.P:
    ...     print(p)
    [[0.96703297 0.03296703 0.         0.         0.        ]
     [0.10638298 0.68085106 0.21276596 0.         0.        ]
     [0.         0.14285714 0.7755102  0.08163265 0.        ]
     [0.         0.         0.5        0.5        0.        ]
     [0.         0.         0.         0.         1.        ]]
    [[0.88636364 0.10606061 0.00757576 0.         0.        ]
     [0.04402516 0.89308176 0.06289308 0.         0.        ]
     [0.         0.05882353 0.8627451  0.07843137 0.        ]
     [0.         0.         0.13846154 0.86153846 0.        ]
     [0.         0.         0.         0.         1.        ]]
    [[0.78082192 0.17808219 0.02739726 0.01369863 0.        ]
     [0.03488372 0.90406977 0.05813953 0.00290698 0.        ]
     [0.         0.05919003 0.84735202 0.09034268 0.00311526]
     [0.         0.         0.05811623 0.92985972 0.01202405]
     [0.         0.         0.         0.14285714 0.85714286]]
    [[0.82692308 0.15384615 0.         0.01923077 0.        ]
     [0.0703125  0.7890625  0.125      0.015625   0.        ]
     [0.00295858 0.06213018 0.82248521 0.10946746 0.00295858]
     [0.         0.00185529 0.07606679 0.88497217 0.03710575]
     [0.         0.         0.         0.07803468 0.92196532]]
    [[1.         0.         0.         0.         0.        ]
     [0.         1.         0.         0.         0.        ]
     [0.         0.06666667 0.9        0.03333333 0.        ]
     [0.         0.         0.05660377 0.90566038 0.03773585]
     [0.         0.         0.         0.03932584 0.96067416]]
    >>> sm.S[0]
    array([[0.54148249, 0.16780007, 0.24991499, 0.04080245, 0.        ],
           [0.        , 0.        , 0.        , 0.        , 1.        ]])
    >>> sm.S[2]
    array([0.03607655, 0.22667277, 0.25883041, 0.43607249, 0.04234777])

    (4) Spatial_Markov also accept discrete time series and calculate
    categorical spatial lags on which several transition probability matrices
    are conditioned.
    Let's still use the US state income time series to demonstrate. We first
    discretize them into categories and then pass them to Spatial_Markov.

    >>> import mapclassify as mc
    >>> y = mc.Quantiles(rpci.flatten(), k=5).yb.reshape(rpci.shape)
    >>> np.random.seed(5)
    >>> sm = Spatial_Markov(y, w, discrete=True, variable_name='discretized rpci')
    >>> sm.k
    5
    >>> sm.m
    5
    >>> for p in sm.P:
    ...     print(p)
    [[0.94787645 0.04440154 0.00772201 0.         0.        ]
     [0.08333333 0.81060606 0.10606061 0.         0.        ]
     [0.         0.12765957 0.79787234 0.07446809 0.        ]
     [0.         0.02777778 0.22222222 0.66666667 0.08333333]
     [0.         0.         0.         0.33333333 0.66666667]]
    [[0.888      0.096      0.016      0.         0.        ]
     [0.06049822 0.84341637 0.09608541 0.         0.        ]
     [0.00666667 0.10666667 0.81333333 0.07333333 0.        ]
     [0.         0.         0.08527132 0.86821705 0.04651163]
     [0.         0.         0.         0.10204082 0.89795918]]
    [[0.65217391 0.32608696 0.02173913 0.         0.        ]
     [0.07446809 0.80851064 0.11170213 0.         0.00531915]
     [0.01071429 0.1        0.76428571 0.11785714 0.00714286]
     [0.         0.00552486 0.09392265 0.86187845 0.03867403]
     [0.         0.         0.         0.13157895 0.86842105]]
    [[0.91935484 0.06451613 0.         0.01612903 0.        ]
     [0.06796117 0.90291262 0.02912621 0.         0.        ]
     [0.         0.05755396 0.87769784 0.0647482  0.        ]
     [0.         0.02150538 0.10752688 0.80107527 0.06989247]
     [0.         0.         0.         0.08064516 0.91935484]]
    [[0.81818182 0.18181818 0.         0.         0.        ]
     [0.01754386 0.70175439 0.26315789 0.01754386 0.        ]
     [0.         0.14285714 0.73333333 0.12380952 0.        ]
     [0.         0.0042735  0.06837607 0.89316239 0.03418803]
     [0.         0.         0.         0.03891051 0.96108949]]

    """

    def __init__(
        self,
        y,
        w,
        k=4,
        m=4,
        permutations=0,
        fixed=True,
        discrete=False,
        cutoffs=None,
        lag_cutoffs=None,
        variable_name=None,
        fill_empty_classes=False,
    ):

        y = np.asarray(y)
        self.fixed = fixed
        self.discrete = discrete
        self.cutoffs = cutoffs
        self.m = m
        self.lag_cutoffs = lag_cutoffs
        self.variable_name = variable_name

        if discrete:
            merged = list(itertools.chain.from_iterable(y))
            classes = np.unique(merged)
            self.classes = classes
            self.k = len(classes)
            self.m = self.k
            label_dict = dict(zip(classes, range(self.k)))
            y_int = []
            for yi in y:
                y_int.append(list(map(label_dict.get, yi)))
            self.class_ids = np.array(y_int)
            self.lclass_ids = self.class_ids
        else:
            self.class_ids, self.cutoffs, self.k = self._maybe_classify(
                y, k=k, cutoffs=self.cutoffs
            )
            self.classes = np.arange(self.k)

        classic = Markov(
            self.class_ids, fill_empty_classes=fill_empty_classes, summary=False
        )
        self.p = classic.p
        self.transitions = classic.transitions
        self.T, self.P = self._calc(y, w, fill_empty_classes=fill_empty_classes)

        if permutations:
            nrp = np.random.permutation
            counter = 0
            x2_realizations = np.zeros((permutations, 1))
            for perm in range(permutations):
                T, P = self._calc(nrp(y), w)
                x2 = [chi2(T[i], self.transitions)[0] for i in range(self.k)]
                x2s = sum(x2)
                x2_realizations[perm] = x2s
                if x2s >= self.x2:
                    counter += 1
            self.x2_rpvalue = (counter + 1.0) / (permutations + 1.0)
            self.x2_realizations = x2_realizations

    @property
    def s(self):
        if not hasattr(self, "_s"):
            self._s = steady_state(self.p)
        return self._s

    @property
    def S(self):
        if not hasattr(self, "_S"):
            _S = []
            for i, p in enumerate(self.P):
                _S.append(steady_state(p))
            # if np.array(_S).dtype is np.dtype('O'):
            self._S = np.asarray(_S)
        return self._S

    @property
    def f(self):
        if not hasattr(self, "_f"):
            self._f = fmpt(self.p)
        return self._f

    @property
    def F(self):
        if not hasattr(self, "_F"):
            F = np.zeros_like(self.P)
            for i, p in enumerate(self.P):
                F[i] = fmpt(np.asarray(p))
            self._F = np.asarray(F)
        return self._F

    # bickenbach and bode tests
    @property
    def ht(self):
        if not hasattr(self, "_ht"):
            self._ht = homogeneity(self.T)
        return self._ht

    @property
    def Q(self):
        if not hasattr(self, "_Q"):
            self._Q = self.ht.Q
        return self._Q

    @property
    def Q_p_value(self):
        self._Q_p_value = self.ht.Q_p_value
        return self._Q_p_value

    @property
    def LR(self):
        self._LR = self.ht.LR
        return self._LR

    @property
    def LR_p_value(self):
        self._LR_p_value = self.ht.LR_p_value
        return self._LR_p_value

    @property
    def dof_hom(self):
        self._dof_hom = self.ht.dof
        return self._dof_hom

    # shtests
    @property
    def shtest(self):
        if not hasattr(self, "_shtest"):
            self._shtest = self._mn_test()
        return self._shtest

    @property
    def chi2(self):
        if not hasattr(self, "_chi2"):
            self._chi2 = self._chi2_test()
        return self._chi2

    @property
    def x2(self):
        if not hasattr(self, "_x2"):
            self._x2 = sum([c[0] for c in self.chi2])
        return self._x2

    @property
    def x2_pvalue(self):
        if not hasattr(self, "_x2_pvalue"):
            self._x2_pvalue = 1 - stats.chi2.cdf(self.x2, self.x2_dof)
        return self._x2_pvalue

    @property
    def x2_dof(self):
        if not hasattr(self, "_x2_dof"):
            k = self.k
            self._x2_dof = k * (k - 1) * (k - 1)
        return self._x2_dof

    def _calc(self, y, w, fill_empty_classes=False):
        """Helper to estimate spatial lag conditioned Markov transition
        probability matrices based on maximum likelihood techniques.

        If fill_empty_classes=True, assign 1 to diagonal elements which fall in rows
        full of 0s to ensure each conditional transition probability matrix
        is a stochastic matrix (each row sums up to 1).

        """
        if self.discrete:
            self.lclass_ids = weights.lag_categorical(w, self.class_ids, ties="tryself")
        else:
            ly = weights.lag_spatial(w, y)
            self.lclass_ids, self.lag_cutoffs, self.m = self._maybe_classify(
                ly, self.m, self.lag_cutoffs
            )
            self.lclasses = np.arange(self.m)

        T = np.zeros((self.m, self.k, self.k))
        n, t = y.shape
        for t1 in range(t - 1):
            t2 = t1 + 1
            for i in range(n):
                T[
                    self.lclass_ids[i, t1], self.class_ids[i, t1], self.class_ids[i, t2]
                ] += 1

        P = np.zeros_like(T)
        for i, mat in enumerate(T):
            row_sum = mat.sum(axis=1)
            row_sum = row_sum + (row_sum == 0)
            p_i = np.array(np.diag(1.0 / row_sum)).dot(np.array(mat))
            P[i] = p_i

        if fill_empty_classes:
            P = fill_empty_diagonals(P)
        return T, P

    def _mn_test(self):
        """
        helper to calculate tests of differences between steady state
        distributions from the conditional and overall distributions.
        """
        n0, n1, n2 = self.T.shape
        rn = list(range(n0))
        mat = [self._ssmnp_test(self.s, self.S[i], self.T[i].sum()) for i in rn]
        return mat

    def _ssmnp_test(self, p1, p2, nt):
        """
        Steady state multinomial probability difference test.

        Arguments
        ---------
        p1       :  array
                    (k, ), first steady state probability distribution.
        p1       :  array
                    (k, ), second steady state probability distribution.
        nt       :  int
                    number of transitions to base the test on.

        Returns
        -------
        tuple
                   (3 elements)
                   (chi2 value, pvalue, degrees of freedom)

        """

        o = nt * p2
        e = nt * p1
        d = np.multiply((o - e), (o - e))
        d = d / e
        chi2 = d.sum()
        pvalue = 1 - stats.chi2.cdf(chi2, self.k - 1)
        return (chi2, pvalue, self.k - 1)

    def _chi2_test(self):
        """
        helper to calculate tests of differences between the conditional
        transition matrices and the overall transitions matrix.
        """
        n0, n1, n2 = self.T.shape
        rn = list(range(n0))
        mat = [chi2(self.T[i], self.transitions) for i in rn]
        return mat

    def summary(self, file_name=None):
        """
        A summary method to call the Markov homogeneity test to test for
        temporally lagged spatial dependence.

        To learn more about the properties of the tests, refer to
        :cite:`Rey2016a` and :cite:`Kang2018`.
        """

        class_names = ["C%d" % i for i in range(self.k)]
        regime_names = ["LAG%d" % i for i in range(self.k)]
        ht = homogeneity(self.T, class_names=class_names, regime_names=regime_names)
        title = "Spatial Markov Test"
        if self.variable_name:
            title = title + ": " + self.variable_name
        if file_name:
            ht.summary(file_name=file_name, title=title)
        else:
            ht.summary(title=title)

    def _maybe_classify(self, y, k, cutoffs):
        """Helper method for classifying continuous data.

        """

        rows, cols = y.shape
        if cutoffs is None:
            if self.fixed:
                mcyb = mc.Quantiles(y.flatten(), k=k)
                yb = mcyb.yb.reshape(y.shape)
                cutoffs = mcyb.bins
                k = len(cutoffs)
                return yb, cutoffs[:-1], k
            else:
                yb = np.array(
                    [mc.Quantiles(y[:, i], k=k).yb for i in np.arange(cols)]
                ).transpose()
                return yb, None, k
        else:
            cutoffs = list(cutoffs) + [np.inf]
            cutoffs = np.array(cutoffs)
            yb = mc.UserDefined(y.flatten(), np.array(cutoffs)).yb.reshape(y.shape)
            k = len(cutoffs)
            return yb, cutoffs[:-1], k


def chi2(T1, T2):
    """
    chi-squared test of difference between two transition matrices.

    Parameters
    ----------
    T1    : array
            (k, k), matrix of transitions (counts).
    T2    : array
            (k, k), matrix of transitions (counts) to use to form the
            probabilities under the null.

    Returns
    -------
          : tuple
            (3 elements).
            (chi2 value, pvalue, degrees of freedom).

    Examples
    --------
    >>> import libpysal
    >>> from giddy.markov import Spatial_Markov, chi2
    >>> f = libpysal.io.open(libpysal.examples.get_path("usjoin.csv"))
    >>> years = list(range(1929, 2010))
    >>> pci = np.array([f.by_col[str(y)] for y in years]).transpose()
    >>> rpci = pci/(pci.mean(axis=0))
    >>> w = libpysal.io.open(libpysal.examples.get_path("states48.gal")).read()
    >>> w.transform='r'
    >>> sm = Spatial_Markov(rpci, w, fixed=True)
    >>> T1 = sm.T[0]
    >>> T1
    array([[562.,  22.,   1.,   0.],
           [ 12., 201.,  22.,   0.],
           [  0.,  17.,  97.,   4.],
           [  0.,   0.,   3.,  19.]])
    >>> T2 = sm.transitions
    >>> T2
    array([[884.,  77.,   4.,   0.],
           [ 68., 794.,  87.,   3.],
           [  1.,  92., 815.,  51.],
           [  1.,   0.,  60., 903.]])
    >>> chi2(T1,T2)
    (23.39728441473295, 0.005363116704861337, 9)

    Notes
    -----
    Second matrix is used to form the probabilities under the null.
    Marginal sums from first matrix are distributed across these probabilities
    under the null. In other words the observed transitions are taken from T1
    while the expected transitions are formed as follows

    .. math::

            E_{i,j} = \sum_j T1_{i,j} * T2_{i,j}/\sum_j T2_{i,j}

    Degrees of freedom corrected for any rows in either T1 or T2 that have
    zero total transitions.
    """
    rs2 = T2.sum(axis=1)
    rs1 = T1.sum(axis=1)
    rs2nz = rs2 > 0
    rs1nz = rs1 > 0
    dof1 = sum(rs1nz)
    dof2 = sum(rs2nz)
    rs2 = rs2 + (rs2 == 0)
    dof = (dof1 - 1) * (dof2 - 1)
    p = np.diag(1 / rs2).dot(np.array(T2))
    E = np.diag(rs1).dot(np.array(p))
    num = T1 - E
    num = np.multiply(num, num)
    E = E + (E == 0)
    chi2 = num / E
    chi2 = chi2.sum()
    pvalue = 1 - stats.chi2.cdf(chi2, dof)
    return chi2, pvalue, dof


class LISA_Markov(Markov):
    """
    Markov for Local Indicators of Spatial Association

    Parameters
    ----------
    y                  : array
                         (n, t), n cross-sectional units observed over t time
                         periods.
    w                  : W
                         spatial weights object.
    permutations       : int, optional
                         number of permutations used to determine LISA
                         significance (the default is 0).
    significance_level : float, optional
                         significance level (two-sided) for filtering
                         significant LISA endpoints in a transition (the
                         default is 0.05).
    geoda_quads        : bool
                         If True use GeoDa scheme: HH=1, LL=2, LH=3, HL=4.
                         If False use PySAL Scheme: HH=1, LH=2, LL=3, HL=4.
                         (the default is False).

    Attributes
    ----------
    chi_2        : tuple
                   (3 elements)
                   (chi square test statistic, p-value, degrees of freedom) for
                   test that dynamics of y are independent of dynamics of wy.
    classes      : array
                   (4, 1)
                   1=HH, 2=LH, 3=LL, 4=HL (own, lag)
                   1=HH, 2=LL, 3=LH, 4=HL (own, lag) (if geoda_quads=True)
    expected_t   : array
                   (4, 4), expected number of transitions under the null that
                   dynamics of y are independent of dynamics of wy.
    move_types   : matrix
                   (n, t-1), integer values indicating which type of LISA
                   transition occurred (q1 is quadrant in period 1, q2 is
                   quadrant in period 2).

                   .. table:: Move Types
                      :widths: auto

                      ==  ==     =========
                      q1  q2     move_type
                      ==  ==     =========
                      1   1      1
                      1   2      2
                      1   3      3
                      1   4      4
                      2   1      5
                      2   2      6
                      2   3      7
                      2   4      8
                      3   1      9
                      3   2      10
                      3   3      11
                      3   4      12
                      4   1      13
                      4   2      14
                      4   3      15
                      4   4      16
                      ==  ==     =========

    p            : array
                   (k, k), transition probability matrix.
    p_values     : matrix
                   (n, t), LISA p-values for each end point (if permutations >
                   0).
    significant_moves : matrix
                        (n, t-1), integer values indicating the type and
                        significance of a LISA transition. st = 1 if
                        significant in period t, else st=0 (if permutations >
                        0).

                        .. table:: Significant Moves1

                           ===============  ===================
                           (s1,s2)          move_type
                           ===============  ===================
                           (1,1)            [1, 16]
                           (1,0)            [17, 32]
                           (0,1)            [33, 48]
                           (0,0)            [49, 64]
                           ===============  ===================

                        .. table:: Significant Moves2

                           == ==  ==  ==  =========
                           q1 q2  s1  s2  move_type
                           == ==  ==  ==  =========
                           1  1   1   1   1
                           1  2   1   1   2
                           1  3   1   1   3
                           1  4   1   1   4
                           2  1   1   1   5
                           2  2   1   1   6
                           2  3   1   1   7
                           2  4   1   1   8
                           3  1   1   1   9
                           3  2   1   1   10
                           3  3   1   1   11
                           3  4   1   1   12
                           4  1   1   1   13
                           4  2   1   1   14
                           4  3   1   1   15
                           4  4   1   1   16
                           1  1   1   0   17
                           1  2   1   0   18
                           .  .   .   .    .
                           .  .   .   .    .
                           4  3   1   0   31
                           4  4   1   0   32
                           1  1   0   1   33
                           1  2   0   1   34
                           .  .   .   .    .
                           .  .   .   .    .
                           4  3   0   1   47
                           4  4   0   1   48
                           1  1   0   0   49
                           1  2   0   0   50
                           .  .   .   .    .
                           .  .   .   .    .
                           4  3   0   0   63
                           4  4   0   0   64
                           == ==  ==  ==  =========

    steady_state : array
                   (k, ), ergodic distribution.
    transitions  : array
                   (4, 4), count of transitions between each state i and j.
    spillover    : array
                   (n, 1) binary array, locations that were not part of a
                   cluster in period 1 but joined a prexisting cluster in
                   period 2.

    Examples
    --------
    >>> import libpysal
    >>> import numpy as np
    >>> from giddy.markov import LISA_Markov
    >>> np.set_printoptions(suppress=True) #prevent scientific format
    >>> f = libpysal.io.open(libpysal.examples.get_path("usjoin.csv"))
    >>> years = list(range(1929, 2010))
    >>> pci = np.array([f.by_col[str(y)] for y in years]).transpose()
    >>> w = libpysal.io.open(libpysal.examples.get_path("states48.gal")).read()
    >>> lm = LISA_Markov(pci,w)
    >>> lm.classes
    array([1, 2, 3, 4])
    >>> lm.steady_state
    array([0.28561505, 0.14190226, 0.40493672, 0.16754598])
    >>> lm.transitions
    array([[1087.,   44.,    4.,   34.],
           [  41.,  470.,   36.,    1.],
           [   5.,   34., 1422.,   39.],
           [  30.,    1.,   40.,  552.]])
    >>> lm.p
    array([[0.92985458, 0.03763901, 0.00342173, 0.02908469],
           [0.07481752, 0.85766423, 0.06569343, 0.00182482],
           [0.00333333, 0.02266667, 0.948     , 0.026     ],
           [0.04815409, 0.00160514, 0.06420546, 0.88603531]])
    >>> lm.move_types[0,:3]
    array([11, 11, 11])
    >>> lm.move_types[0,-3:]
    array([11, 11, 11])

    Now consider only moves with one, or both, of the LISA end points being
    significant

    >>> np.random.seed(10)
    >>> lm_random = LISA_Markov(pci, w, permutations=99)
    >>> lm_random.significant_moves[0, :3]
    array([11, 11, 11])
    >>> lm_random.significant_moves[0,-3:]
    array([59, 43, 27])


    Any value less than 49 indicates at least one of the LISA end points was
    significant. So for example, the first spatial unit experienced a
    transition of type 11 (LL, LL)  during the first three and last tree
    intervals (according to lm.move_types), however, the last three of these
    transitions involved insignificant LISAS in both the start and ending year
    of each transition.

    Test whether the moves of y are independent of the moves of wy

    >>> "Chi2: %8.3f, p: %5.2f, dof: %d" % lm.chi_2
    'Chi2: 1058.208, p:  0.00, dof: 9'

    Actual transitions of LISAs

    >>> lm.transitions
    array([[1087.,   44.,    4.,   34.],
           [  41.,  470.,   36.,    1.],
           [   5.,   34., 1422.,   39.],
           [  30.,    1.,   40.,  552.]])

    Expected transitions of LISAs under the null y and wy are moving
    independently of one another

    >>> lm.expected_t
    array([[1123.2809778 ,   11.53773565,    0.34752216,   33.83376439],
           [   3.50272664,  528.47388155,   15.917888  ,    0.10550381],
           [   0.15387808,   23.21635562, 1466.90710117,    9.72266513],
           [   9.60775143,    0.09868563,    6.23537392,  607.05818902]])

    If the LISA classes are to be defined according to GeoDa, the `geoda_quad`
    option has to be set to true

    >>> lm.q[0:5,0]
    array([3, 2, 3, 1, 4])
    >>> lm = LISA_Markov(pci,w, geoda_quads=True)
    >>> lm.q[0:5,0]
    array([2, 3, 2, 1, 4])

    """

    def __init__(
        self, y, w, permutations=0, significance_level=0.05, geoda_quads=False
    ):
        y = y.transpose()
        pml = Moran_Local
        gq = geoda_quads
        ml = [pml(yi, w, permutations=permutations, geoda_quads=gq) for yi in y]
        q = np.array([mli.q for mli in ml]).transpose()
        classes = np.arange(1, 5)  # no guarantee all 4 quadrants are visited
        Markov.__init__(self, q, classes, summary=False)
        self.q = q
        self.w = w
        n, k = q.shape
        k -= 1
        self.significance_level = significance_level
        move_types = np.zeros((n, k), int)
        sm = np.zeros((n, k), int)
        self.significance_level = significance_level
        if permutations > 0:
            p = np.array([mli.p_z_sim for mli in ml]).transpose()
            self.p_values = p
            pb = p <= significance_level
        else:
            pb = np.zeros_like(y.T)
        for t in range(k):
            origin = q[:, t]
            dest = q[:, t + 1]
            p_origin = pb[:, t]
            p_dest = pb[:, t + 1]
            for r in range(n):
                move_types[r, t] = TT[origin[r], dest[r]]
                key = (origin[r], dest[r], p_origin[r], p_dest[r])
                sm[r, t] = MOVE_TYPES[key]
        if permutations > 0:
            self.significant_moves = sm
        self.move_types = move_types

        # null of own and lag moves being independent

        ybar = y.mean(axis=0)
        r = y / ybar
        ylag = np.array([weights.lag_spatial(w, yt) for yt in y])
        rlag = ylag / ybar
        rc = r < 1.0
        rlagc = rlag < 1.0
        markov_y = Markov(rc, summary=False)
        markov_ylag = Markov(rlagc, summary=False)
        A = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1], [0, 1, 0, 0]])

        kp = A.dot(np.kron(markov_y.p, markov_ylag.p)).dot(A.T)
        trans = self.transitions.sum(axis=1)
        t1 = np.diag(trans).dot(kp)
        t2 = self.transitions
        self.chi_2 = chi2(t2, t1)
        self.expected_t = t1
        self.permutations = permutations

    def spillover(self, quadrant=1, neighbors_on=False):
        """
        Detect spillover locations for diffusion in LISA Markov.

        Parameters
        ----------
        quadrant     : int
                       which quadrant in the scatterplot should form the core
                       of a cluster.
        neighbors_on : binary
                       If false, then only the 1st order neighbors of a core
                       location are included in the cluster.
                       If true, neighbors of cluster core 1st order neighbors
                       are included in the cluster.

        Returns
        -------
        results      : dictionary
                       two keys - values pairs:
                       'components' - array (n, t)
                       values are integer ids (starting at 1) indicating which
                       component/cluster observation i in period t belonged to.
                       'spillover' - array (n, t-1)
                       binary values indicating if the location was a
                       spill-over location that became a new member of a
                       previously existing cluster.

        Examples
        --------
        >>> import libpysal
        >>> from giddy.markov import LISA_Markov
        >>> f = libpysal.io.open(libpysal.examples.get_path("usjoin.csv"))
        >>> years = list(range(1929, 2010))
        >>> pci = np.array([f.by_col[str(y)] for y in years]).transpose()
        >>> w = libpysal.io.open(libpysal.examples.get_path("states48.gal")).read()
        >>> np.random.seed(10)
        >>> lm_random = LISA_Markov(pci, w, permutations=99)
        >>> r = lm_random.spillover()
        >>> (r['components'][:, 12] > 0).sum()
        17
        >>> (r['components'][:, 13]>0).sum()
        23
        >>> (r['spill_over'][:,12]>0).sum()
        6

        Including neighbors of core neighbors
        >>> rn = lm_random.spillover(neighbors_on=True)
        >>> (rn['components'][:, 12] > 0).sum()
        26
        >>> (rn["components"][:, 13] > 0).sum()
        34
        >>> (rn["spill_over"][:, 12] > 0).sum()
        8

        """
        n, k = self.q.shape
        if self.permutations:
            spill_over = np.zeros((n, k - 1))
            components = np.zeros((n, k))
            i2id = {}  # handle string keys
            for key in list(self.w.neighbors.keys()):
                idx = self.w.id2i[key]
                i2id[idx] = key
            sig_lisas = (self.q == quadrant) * (
                self.p_values <= self.significance_level
            )
            sig_ids = [np.nonzero(sig_lisas[:, i])[0].tolist() for i in range(k)]

            neighbors = self.w.neighbors
            for t in range(k - 1):
                s1 = sig_ids[t]
                s2 = sig_ids[t + 1]
                g1 = Graph(undirected=True)
                for i in s1:
                    for neighbor in neighbors[i2id[i]]:
                        g1.add_edge(i2id[i], neighbor, 1.0)
                        if neighbors_on:
                            for nn in neighbors[neighbor]:
                                g1.add_edge(neighbor, nn, 1.0)
                components1 = g1.connected_components(op=gt)
                components1 = [list(c.nodes) for c in components1]
                g2 = Graph(undirected=True)
                for i in s2:
                    for neighbor in neighbors[i2id[i]]:
                        g2.add_edge(i2id[i], neighbor, 1.0)
                        if neighbors_on:
                            for nn in neighbors[neighbor]:
                                g2.add_edge(neighbor, nn, 1.0)
                components2 = g2.connected_components(op=gt)
                components2 = [list(c.nodes) for c in components2]
                c2 = []
                c1 = []
                for c in components2:
                    c2.extend(c)
                for c in components1:
                    c1.extend(c)

                new_ids = [j for j in c2 if j not in c1]
                spill_ids = []
                for j in new_ids:
                    # find j's component in period 2
                    cj = [c for c in components2 if j in c][0]
                    # for members of j's component in period 2, check if they
                    # belonged to any components in period 1
                    for i in cj:
                        if i in c1:
                            spill_ids.append(j)
                            break
                for spill_id in spill_ids:
                    id = self.w.id2i[spill_id]
                    spill_over[id, t] = 1
                for c, component in enumerate(components1):
                    for i in component:
                        ii = self.w.id2i[i]
                        components[ii, t] = c + 1
            results = {}
            results["components"] = components
            results["spill_over"] = spill_over
            return results

        else:
            return None


def kullback(F):
    """
    Kullback information based test of Markov Homogeneity.

    Parameters
    ----------
    F : array
        (s, r, r), values are transitions (not probabilities) for
        s strata, r initial states, r terminal states.

    Returns
    -------
    Results : dictionary
              (key - value)

              Conditional homogeneity - (float) test statistic for homogeneity
              of transition probabilities across strata.

              Conditional homogeneity pvalue - (float) p-value for test
              statistic.

              Conditional homogeneity dof - (int) degrees of freedom =
              r(s-1)(r-1).

    Notes
    -----
    Based on :cite:`Kullback1962`.
    Example below is taken from Table 9.2 .

    Examples
    --------
    >>> import numpy as np
    >>> from giddy.markov import kullback
    >>> s1 = np.array([
    ...         [ 22, 11, 24,  2,  2,  7],
    ...         [ 5, 23, 15,  3, 42,  6],
    ...         [ 4, 21, 190, 25, 20, 34],
    ...         [0, 2, 14, 56, 14, 28],
    ...         [32, 15, 20, 10, 56, 14],
    ...         [5, 22, 31, 18, 13, 134]
    ...     ])
    >>> s2 = np.array([
    ...     [3, 6, 9, 3, 0, 8],
    ...     [1, 9, 3, 12, 27, 5],
    ...     [2, 9, 208, 32, 5, 18],
    ...     [0, 14, 32, 108, 40, 40],
    ...     [22, 14, 9, 26, 224, 14],
    ...     [1, 5, 13, 53, 13, 116]
    ...     ])
    >>>
    >>> F = np.array([s1, s2])
    >>> res = kullback(F)
    >>> "%8.3f"%res['Conditional homogeneity']
    ' 160.961'
    >>> "%d"%res['Conditional homogeneity dof']
    '30'
    >>> "%3.1f"%res['Conditional homogeneity pvalue']
    '0.0'

    """

    F1 = F == 0
    F1 = F + F1
    FLF = F * np.log(F1)
    T1 = 2 * FLF.sum()

    FdJK = F.sum(axis=0)
    FdJK1 = FdJK + (FdJK == 0)
    FdJKLFdJK = FdJK * np.log(FdJK1)
    T2 = 2 * FdJKLFdJK.sum()

    FdJd = F.sum(axis=0).sum(axis=1)
    FdJd1 = FdJd + (FdJd == 0)
    T3 = 2 * (FdJd * np.log(FdJd1)).sum()

    FIJd = F[:, :].sum(axis=1)
    FIJd1 = FIJd + (FIJd == 0)
    T4 = 2 * (FIJd * np.log(FIJd1)).sum()

    T6 = F.sum()
    T6 = 2 * T6 * np.log(T6)

    s, r, r1 = F.shape
    chom = T1 - T4 - T2 + T3
    cdof = r * (s - 1) * (r - 1)
    results = {}
    results["Conditional homogeneity"] = chom
    results["Conditional homogeneity dof"] = cdof
    results["Conditional homogeneity pvalue"] = 1 - stats.chi2.cdf(chom, cdof)
    return results


def prais(pmat):
    """
    Prais conditional mobility measure.

    Parameters
    ----------
    pmat : matrix
           (k, k), Markov probability transition matrix.

    Returns
    -------
    pr   : matrix
           (1, k), conditional mobility measures for each of the k classes.

    Notes
    -----
    Prais' conditional mobility measure for a class is defined as:

    .. math::

            pr_i = 1 -  p_{i,i}

    Examples
    --------
    >>> import numpy as np
    >>> import libpysal
    >>> from giddy.markov import Markov,prais
    >>> f = libpysal.io.open(libpysal.examples.get_path("usjoin.csv"))
    >>> pci = np.array([f.by_col[str(y)] for y in range(1929,2010)])
    >>> q5 = np.array([mc.Quantiles(y).yb for y in pci]).transpose()
    >>> m = Markov(q5, summary=False)
    >>> m.transitions
    array([[729.,  71.,   1.,   0.,   0.],
           [ 72., 567.,  80.,   3.,   0.],
           [  0.,  81., 631.,  86.,   2.],
           [  0.,   3.,  86., 573.,  56.],
           [  0.,   0.,   1.,  57., 741.]])
    >>> m.p
    array([[0.91011236, 0.0886392 , 0.00124844, 0.        , 0.        ],
           [0.09972299, 0.78531856, 0.11080332, 0.00415512, 0.        ],
           [0.        , 0.10125   , 0.78875   , 0.1075    , 0.0025    ],
           [0.        , 0.00417827, 0.11977716, 0.79805014, 0.07799443],
           [0.        , 0.        , 0.00125156, 0.07133917, 0.92740926]])
    >>> prais(m.p)
    array([0.08988764, 0.21468144, 0.21125   , 0.20194986, 0.07259074])

    """
    pmat = np.array(pmat)
    pr = 1 - np.diag(pmat)
    return pr


def homogeneity(
    transition_matrices,
    regime_names=[],
    class_names=[],
    title="Markov Homogeneity Test",
):
    """
    Test for homogeneity of Markov transition probabilities across regimes.

    Parameters
    ----------
    transition_matrices : list
                          of transition matrices for regimes, all matrices must
                          have same size (r, c). r is the number of rows in the
                          transition matrix and c is the number of columns in
                          the transition matrix.
    regime_names        : sequence
                          Labels for the regimes.
    class_names         : sequence
                          Labels for the classes/states of the Markov chain.
    title               : string
                          name of test.

    Returns
    -------
                        : implicit
                          an instance of Homogeneity_Results.
    """

    return Homogeneity_Results(
        transition_matrices,
        regime_names=regime_names,
        class_names=class_names,
        title=title,
    )


class Homogeneity_Results:
    """
    Wrapper class to present homogeneity results.

    Parameters
    ----------
    transition_matrices : list
                          of transition matrices for regimes, all matrices must
                          have same size (r, c). r is the number of rows in
                          the transition matrix and c is the number of columns
                          in the transition matrix.
    regime_names        : sequence
                          Labels for the regimes.
    class_names         : sequence
                          Labels for the classes/states of the Markov chain.
    title               : string
                          Title of the table.

    Attributes
    -----------

    Notes
    -----
    Degrees of freedom adjustment follow the approach in :cite:`Bickenbach2003`.

    Examples
    --------
    See Spatial_Markov above.

    """

    def __init__(
        self,
        transition_matrices,
        regime_names=[],
        class_names=[],
        title="Markov Homogeneity Test",
    ):
        self._homogeneity(transition_matrices)
        self.regime_names = regime_names
        self.class_names = class_names
        self.title = title

    def _homogeneity(self, transition_matrices):
        # form null transition probability matrix
        M = np.array(transition_matrices)
        m, r, k = M.shape
        self.k = k
        B = np.zeros((r, m))
        T = M.sum(axis=0)
        self.t_total = T.sum()
        n_i = T.sum(axis=1)
        A_i = (T > 0).sum(axis=1)
        A_im = np.zeros((r, m))
        p_ij = np.dot(np.diag(1.0 / (n_i + (n_i == 0) * 1.0)), T)
        den = p_ij + 1.0 * (p_ij == 0)
        b_i = np.zeros_like(A_i)
        p_ijm = np.zeros_like(M)
        # get dimensions
        m, n_rows, n_cols = M.shape
        m = 0
        Q = 0.0
        LR = 0.0
        lr_table = np.zeros_like(M)
        q_table = np.zeros_like(M)

        for nijm in M:
            nim = nijm.sum(axis=1)
            B[:, m] = 1.0 * (nim > 0)
            b_i = b_i + 1.0 * (nim > 0)
            p_ijm[m] = np.dot(np.diag(1.0 / (nim + (nim == 0) * 1.0)), nijm)
            num = (p_ijm[m] - p_ij) ** 2
            ratio = num / den
            qijm = np.dot(np.diag(nim), ratio)
            q_table[m] = qijm
            Q = Q + qijm.sum()
            # only use nonzero pijm in lr test
            mask = (nijm > 0) * (p_ij > 0)
            A_im[:, m] = (nijm > 0).sum(axis=1)
            unmask = 1.0 * (mask == 0)
            ratio = (mask * p_ijm[m] + unmask) / (mask * p_ij + unmask)
            lr = nijm * np.log(ratio)
            LR = LR + lr.sum()
            lr_table[m] = 2 * lr
            m += 1
        # b_i is the number of regimes that have non-zero observations in row i
        # A_i is the number of non-zero elements in row i of the aggregated
        # transition matrix
        self.dof = int(((b_i - 1) * (A_i - 1)).sum())
        self.Q = Q
        self.Q_p_value = 1 - stats.chi2.cdf(self.Q, self.dof)
        self.LR = LR * 2.0
        self.LR_p_value = 1 - stats.chi2.cdf(self.LR, self.dof)
        self.A = A_i
        self.A_im = A_im
        self.B = B
        self.b_i = b_i
        self.LR_table = lr_table
        self.Q_table = q_table
        self.m = m
        self.p_h0 = p_ij
        self.p_h1 = p_ijm

    def summary(self, file_name=None, title="Markov Homogeneity Test"):
        regime_names = ["%d" % i for i in range(self.m)]
        if self.regime_names:
            regime_names = self.regime_names
        cols = ["P(%s)" % str(regime) for regime in regime_names]
        if not self.class_names:
            self.class_names = list(range(self.k))

        max_col = max([len(col) for col in cols])
        col_width = max([5, max_col])  # probabilities have 5 chars
        n_tabs = self.k
        width = n_tabs * 4 + (self.k + 1) * col_width
        lead = "-" * width
        head = title.center(width)
        contents = [lead, head, lead]
        l = "Number of regimes: %d" % int(self.m)
        k = "Number of classes: %d" % int(self.k)
        r = "Regime names: "
        r += ", ".join(regime_names)
        t = "Number of transitions: %d" % int(self.t_total)
        contents.append(k)
        contents.append(t)
        contents.append(l)
        contents.append(r)
        contents.append(lead)
        h = "%7s %20s %20s" % ("Test", "LR", "Chi-2")
        contents.append(h)
        stat = "%7s %20.3f %20.3f" % ("Stat.", self.LR, self.Q)
        contents.append(stat)
        stat = "%7s %20d %20d" % ("DOF", self.dof, self.dof)
        contents.append(stat)
        stat = "%7s %20.3f %20.3f" % ("p-value", self.LR_p_value, self.Q_p_value)
        contents.append(stat)
        print(("\n".join(contents)))
        print(lead)

        cols = ["P(%s)" % str(regime) for regime in self.regime_names]
        if not self.class_names:
            self.class_names = list(range(self.k))
        cols.extend(["%s" % str(cname) for cname in self.class_names])

        max_col = max([len(col) for col in cols])
        col_width = max([5, max_col])  # probabilities have 5 chars
        p0 = []
        line0 = ["{s: <{w}}".format(s="P(H0)", w=col_width)]
        line0.extend(
            (["{s: >{w}}".format(s=cname, w=col_width) for cname in self.class_names])
        )
        print(("    ".join(line0)))
        p0.append("&".join(line0))
        for i, row in enumerate(self.p_h0):
            line = ["%*s" % (col_width, str(self.class_names[i]))]
            line.extend(["%*.3f" % (col_width, v) for v in row])
            print(("    ".join(line)))
            p0.append("&".join(line))
        pmats = [p0]

        print(lead)
        for r, p1 in enumerate(self.p_h1):
            p0 = []
            line0 = ["{s: <{w}}".format(s="P(%s)" % regime_names[r], w=col_width)]
            line0.extend(
                (
                    [
                        "{s: >{w}}".format(s=cname, w=col_width)
                        for cname in self.class_names
                    ]
                )
            )
            print(("    ".join(line0)))
            p0.append("&".join(line0))
            for i, row in enumerate(p1):
                line = ["%*s" % (col_width, str(self.class_names[i]))]
                line.extend(["%*.3f" % (col_width, v) for v in row])
                print(("    ".join(line)))
                p0.append("&".join(line))
            pmats.append(p0)
            print(lead)

        if file_name:
            k = self.k
            ks = str(k + 1)
            with open(file_name, "w") as f:
                c = []
                fmt = "r" * (k + 1)
                s = "\\begin{tabular}{|%s|}\\hline\n" % fmt
                s += "\\multicolumn{%s}{|c|}{%s}" % (ks, title)
                c.append(s)
                s = "Number of classes: %d" % int(self.k)
                c.append("\\hline\\multicolumn{%s}{|l|}{%s}" % (ks, s))
                s = "Number of transitions: %d" % int(self.t_total)
                c.append("\\multicolumn{%s}{|l|}{%s}" % (ks, s))
                s = "Number of regimes: %d" % int(self.m)
                c.append("\\multicolumn{%s}{|l|}{%s}" % (ks, s))
                s = "Regime names: "
                s += ", ".join(regime_names)
                c.append("\\multicolumn{%s}{|l|}{%s}" % (ks, s))
                s = "\\hline\\multicolumn{2}{|l}{%s}" % ("Test")
                s += "&\\multicolumn{2}{r}{LR}&\\multicolumn{2}{r|}{Q}"
                c.append(s)
                s = "Stat."
                s = "\\multicolumn{2}{|l}{%s}" % (s)
                s += "&\\multicolumn{2}{r}{%.3f}" % self.LR
                s += "&\\multicolumn{2}{r|}{%.3f}" % self.Q
                c.append(s)
                s = "\\multicolumn{2}{|l}{%s}" % ("DOF")
                s += "&\\multicolumn{2}{r}{%d}" % int(self.dof)
                s += "&\\multicolumn{2}{r|}{%d}" % int(self.dof)
                c.append(s)
                s = "\\multicolumn{2}{|l}{%s}" % ("p-value")
                s += "&\\multicolumn{2}{r}{%.3f}" % self.LR_p_value
                s += "&\\multicolumn{2}{r|}{%.3f}" % self.Q_p_value
                c.append(s)
                s1 = "\\\\\n".join(c)
                s1 += "\\\\\n"
                c = []
                for mat in pmats:
                    c.append("\\hline\n")
                    for row in mat:
                        c.append(row + "\\\\\n")
                c.append("\\hline\n")
                c.append("\\end{tabular}")
                s2 = "".join(c)
                f.write(s1 + s2)


class FullRank_Markov(Markov):
    """
    Full Rank Markov in which ranks are considered as Markov states rather
    than quantiles or other discretized classes. This is one way to avoid
    issues associated with discretization.

    Parameters
    ----------
    y            : array
                   (n, t) with t>>n, one row per observation (n total),
                   one column recording the value of each observation,
                   with as many columns as time periods.
    fill_empty_classes: bool
                        If True, assign 1 to diagonal elements which fall in rows
                        full of 0s to ensure p is a stochastic transition
                        probability matrix (each row sums up to 1).
    summary      : bool
                   If True, print out the summary of the Markov Chain during
                   initialization. Default is True.

    Attributes
    ----------
    ranks        : array
                   ranks of the original y array (by columns): higher values
                   rank higher, e.g. the largest value in a column ranks 1.
    p            : array
                   (n, n), transition probability matrix for Full
                   Rank Markov.
    steady_state : array
                   (n, ), ergodic distribution.
    transitions  : array
                   (n, n), count of transitions between each rank i and j
    fmpt         : array
                   (n, n), first mean passage times.
    sojourn_time : array
                   (n, ), sojourn times.

    Notes
    -----
    Refer to :cite:`Rey2014a` Equation (11) for details. Ties are resolved by
    assigning distinct ranks, corresponding to the order that the values occur
    in each cross section.

    Examples
    --------
    US nominal per capita income 48 states 81 years 1929-2009

    >>> from giddy.markov import FullRank_Markov
    >>> import libpysal as ps
    >>> import numpy as np
    >>> f = ps.io.open(ps.examples.get_path("usjoin.csv"))
    >>> pci = np.array([f.by_col[str(y)] for y in range(1929,2010)]).transpose()
    >>> m = FullRank_Markov(pci)
    The Markov Chain is irreducible and is composed by:
    1 Recurrent class (indices):
    [ 0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23
     24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47]
    0 Transient classes.
    The Markov Chain has 0 absorbing states.
    >>> m.transitions
    array([[66.,  5.,  5., ...,  0.,  0.,  0.],
           [ 8., 51.,  9., ...,  0.,  0.,  0.],
           [ 2., 13., 44., ...,  0.,  0.,  0.],
           ...,
           [ 0.,  0.,  0., ..., 40., 17.,  0.],
           [ 0.,  0.,  0., ..., 15., 54.,  2.],
           [ 0.,  0.,  0., ...,  2.,  1., 77.]])
    >>> m.p[0, :5]
    array([0.825 , 0.0625, 0.0625, 0.025 , 0.025 ])
    >>> m.fmpt[0, :5]
    array([48.        , 87.96280048, 68.1089084 , 58.83306575, 41.77250827])
    >>> m.sojourn_time[:5]
    array([5.71428571, 2.75862069, 2.22222222, 1.77777778, 1.66666667])

    """

    def __init__(self, y, fill_empty_classes=False, summary=True):

        y = np.asarray(y)
        # resolve ties: All values are given a distinct rank, corresponding
        # to the order that the values occur in each cross section.
        r_asc = np.array([rankdata(col, method="ordinal") for col in y.T]).T
        # ranks by high (1) to low (n)
        self.ranks = r_asc.shape[0] - r_asc + 1
        super(FullRank_Markov, self).__init__(
            self.ranks, fill_empty_classes=fill_empty_classes, summary=summary
        )


def sojourn_time(p, summary=True):
    """
    Calculate sojourn time based on a given transition probability matrix.

    Parameters
    ----------
    p        : array
               (k, k), a Markov transition probability matrix.
    summary  : bool
               If True and the Markov Chain has absorbing states whose
               sojourn time is infinitely large, print out the information
               about the absorbing states. Default is True.
    Returns
    -------
             : array
               (k, ), sojourn times. Each element is the expected time a Markov
               chain spends in each state before leaving that state.

    Notes
    -----
    Refer to :cite:`Ibe2009` for more details on sojourn times for Markov
    chains.

    Examples
    --------
    >>> from giddy.markov import sojourn_time
    >>> import numpy as np
    >>> p = np.array([[.5, .25, .25], [.5, 0, .5], [.25, .25, .5]])
    >>> sojourn_time(p)
    array([2., 1., 2.])

    Non-ergodic Markov Chains with rows full of 0

    >>> p = np.array([[.5, .25, .25], [.5, 0, .5],[ 0, 0, 0]])
    >>> sojourn_time(p)
    Sojourn times are infinite for absorbing states! In this Markov Chain, states [2] are absorbing states.
    array([ 2.,  1., inf])
    """

    p = np.asarray(p)
    if (p.sum(axis=1) == 0).sum() > 0:
        p = fill_empty_diagonals(p)

    markovchain = qe.MarkovChain(p)
    pii = p.diagonal()

    if not (1 - pii).all():
        absorbing_states = np.where(pii == 1)[0]
        non_absorbing_states = np.where(pii != 1)[0]
        st = np.full(len(pii), np.inf)
        if summary:
            print(
                "Sojourn times are infinite for absorbing states! In this "
                "Markov Chain, states {} are absorbing states.".format(
                    list(absorbing_states)
                )
            )
        st[non_absorbing_states] = 1 / (1 - pii[non_absorbing_states])
    else:
        st = 1 / (1 - pii)
    return st


class GeoRank_Markov(Markov):
    """
    Geographic Rank Markov.
    Geographic units are considered as Markov states.

    Parameters
    ----------
    y            : array
                   (n, t) with t>>n, one row per observation (n total),
                   one column recording the value of each observation,
                   with as many columns as time periods.
    fill_empty_classes: bool
                        If True, assign 1 to diagonal elements which fall in rows
                        full of 0s to ensure p is a stochastic transition
                        probability matrix (each row sums up to 1).
    summary      : bool
                   If True, print out the summary of the Markov Chain during
                   initialization. Default is True.

    Attributes
    ----------
    p            : array
                   (n, n), transition probability matrix for
                   geographic rank Markov.
    steady_state : array
                   (n, ), ergodic distribution.
    transitions  : array
                   (n, n), count of rank transitions between each
                   geographic unit i and j.
    fmpt         : array
                   (n, n), first mean passage times.
    sojourn_time : array
                   (n, ), sojourn times.

    Notes
    -----
    Refer to :cite:`Rey2014a` Equation (13)-(16) for details. Ties are
    resolved by assigning distinct ranks, corresponding to the order
    that the values occur in each cross section.

    Examples
    --------
    US nominal per capita income 48 states 81 years 1929-2009

    >>> from giddy.markov import GeoRank_Markov
    >>> import libpysal as ps
    >>> import numpy as np
    >>> f = ps.io.open(ps.examples.get_path("usjoin.csv"))
    >>> pci = np.array([f.by_col[str(y)] for y in range(1929,2010)]).transpose()
    >>> m = GeoRank_Markov(pci)
    The Markov Chain is irreducible and is composed by:
    1 Recurrent class (indices):
    [ 0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23
     24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47]
    0 Transient classes.
    The Markov Chain has 0 absorbing states.
    >>> m.transitions
    array([[38.,  0.,  8., ...,  0.,  0.,  0.],
           [ 0., 15.,  0., ...,  0.,  1.,  0.],
           [ 6.,  0., 44., ...,  5.,  0.,  0.],
           ...,
           [ 2.,  0.,  5., ..., 34.,  0.,  0.],
           [ 0.,  0.,  0., ...,  0., 18.,  2.],
           [ 0.,  0.,  0., ...,  0.,  3., 14.]])
    >>> m.p
    array([[0.475 , 0.    , 0.1   , ..., 0.    , 0.    , 0.    ],
           [0.    , 0.1875, 0.    , ..., 0.    , 0.0125, 0.    ],
           [0.075 , 0.    , 0.55  , ..., 0.0625, 0.    , 0.    ],
           ...,
           [0.025 , 0.    , 0.0625, ..., 0.425 , 0.    , 0.    ],
           [0.    , 0.    , 0.    , ..., 0.    , 0.225 , 0.025 ],
           [0.    , 0.    , 0.    , ..., 0.    , 0.0375, 0.175 ]])
    >>> m.fmpt
    array([[ 48.        ,  63.35532038,  92.75274652, ...,  82.47515731,
             71.01114491,  68.65737127],
           [108.25928005,  48.        , 127.99032986, ...,  92.03098299,
             63.36652935,  61.82733039],
           [ 76.96801786,  64.7713783 ,  48.        , ...,  73.84595169,
             72.24682723,  69.77497173],
           ...,
           [ 93.3107474 ,  62.47670463, 105.80634118, ...,  48.        ,
             69.30121319,  67.08838421],
           [113.65278078,  61.1987031 , 133.57991745, ...,  96.0103924 ,
             48.        ,  56.74165107],
           [114.71894813,  63.4019776 , 134.73381719, ...,  97.287895  ,
             61.45565054,  48.        ]])
    >>> m.sojourn_time
    array([ 1.9047619 ,  1.23076923,  2.22222222,  1.73913043,  1.15942029,
            3.80952381,  1.70212766,  1.25      ,  1.31147541,  1.11111111,
            1.73913043,  1.37931034,  1.17647059,  1.21212121,  1.33333333,
            1.37931034,  1.09589041,  2.10526316,  2.        ,  1.45454545,
            1.26984127, 26.66666667,  1.19402985,  1.23076923,  1.09589041,
            1.56862745,  1.26984127,  2.42424242,  1.50943396,  2.        ,
            1.29032258,  1.09589041,  1.6       ,  1.42857143,  1.25      ,
            1.45454545,  1.29032258,  1.6       ,  1.17647059,  1.56862745,
            1.25      ,  1.37931034,  1.45454545,  1.42857143,  1.29032258,
            1.73913043,  1.29032258,  1.21212121])

    """

    def __init__(self, y, fill_empty_classes=False, summary=True):
        y = np.asarray(y)
        n = y.shape[0]
        # resolve ties: All values are given a distinct rank, corresponding
        # to the order that the values occur in each cross section.
        ranks = np.array([rankdata(col, method="ordinal") for col in y.T]).T
        geo_ranks = np.argsort(ranks, axis=0) + 1
        super(GeoRank_Markov, self).__init__(
            geo_ranks, fill_empty_classes=fill_empty_classes, summary=summary
        )
