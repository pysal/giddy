"""
Directional Analysis of Dynamic LISAs

"""
__author__ = "Sergio J. Rey <sjsrey@gmail.com>"

__all__ = ['Rose']

import numpy as np
from libpysal.api import lag_spatial

POS8 = np.array([1, 1, 0, 0, 1, 1, 0, 0])
POS4 = np.array([1, 0, 1, 0])
NEG8 = 1 - POS8
NEG4 = 1 - POS4


class Rose(object):
    def __init__(self, Y, w, k=8):
        """
        Calculation of rose diagram for local indicators of spatial
        association.

        Parameters
        ----------
        Y             : array
                        (n, 2), variable observed on n spatial units over 2
                        time periods
        w             : W
                        spatial weights object.
        k             : int, optional
                        number of circular sectors in rose diagram (the default
                        is 8).
        permutations  : int, optional
                        number of random spatial permutations for calculation
                        of pseudo p-values (the default is 0).

        Returns
        -------
        results       : dictionary
                        (keys defined below)
        counts        : array
                        (k, 1), number of vectors with angular movement falling
                        in each sector.
        cuts          : array
                        (k, 1), intervals defining circular sectors (in
                        radians).
        random_counts : array
                        (permutations, k), counts from random permutations.
        pvalues       : array
                        (k, 1), one sided (upper tail) pvalues for observed
                        counts.

        Notes
        -----
        Based on [Rey2011]_ .

        Examples
        --------
        Constructing data for illustration of directional LISA analytics.
        Data is for the 48 lower US states over the period 1969-2009 and
        includes per capita income normalized to the national average.

        Load comma delimited data file in and convert to a numpy array

        >>> import libpysal
        >>> f=open(libpysal.examples.get_path("spi_download.csv"),'r')
        >>> lines=f.readlines()
        >>> f.close()
        >>> lines=[line.strip().split(",") for line in lines]
        >>> names=[line[2] for line in lines[1:-5]]
        >>> data=np.array([map(int,line[3:]) for line in lines[1:-5]])

        Bottom of the file has regional data which we don't need for this
        example so we will subset only those records that match a state name

        >>> sids=range(60)
        >>> out=['"United States 3/"',
        ...      '"Alaska 3/"',
        ...      '"District of Columbia"',
        ...      '"Hawaii 3/"',
        ...      '"New England"',
        ...      '"Mideast"',
        ...      '"Great Lakes"',
        ...      '"Plains"',
        ...      '"Southeast"',
        ...      '"Southwest"',
        ...      '"Rocky Mountain"',
        ...      '"Far West 3/"']
        >>> snames=[name for name in names if name not in out]
        >>> sids=[names.index(name) for name in snames]
        >>> states=data[sids,:]
        >>> us=data[0]
        >>> years=np.arange(1969,2009)

        Now we convert state incomes to express them relative to the national
        average

        >>> rel=states/(us*1.)

        Create our contiguity matrix from an external GAL file and row
        standardize the resulting weights

        >>> gal=libpysal.open(libpysal.examples.get_path('states48.gal'))
        >>> w=gal.read()
        >>> w.transform='r'

        Take the first and last year of our income data as the interval to do
        the directional directional analysis

        >>> Y=rel[:,[0,-1]]

        Set the random seed generator which is used in the permutation based
        inference for the rose diagram so that we can replicate our example
        results

        >>> np.random.seed(100)

        Call the rose function to construct the directional histogram for the
        dynamic LISA statistics. We will use four circular sectors for our
        histogram

        >>> r4=Rose(Y,w,k=4)

        What are the cut-offs for our histogram - in radians

        >>> r4.cuts
        array([ 0.        ,  1.57079633,  3.14159265,  4.71238898,  6.28318531])

        How many vectors fell in each sector

        >>> r4.counts
        array([32,  5,  9,  2])

        We can test whether these counts are different than what would be
        expected if there was no association between the movement of the focal
        unit and its spatial lag.

        To do so we call the `permute` method of the object

        >>> r4.permute()

        and then inspect the `p` attibute:

        >>> r4.p
        array([ 0.04,  0.  ,  0.02,  0.  ])

        Repeat the exercise but now for 8 rather than 4 sectors

        >>> r8 = Rose(Y, w, k=8)
        >>> r8.counts
        array([19, 13,  3,  2,  7,  2,  1,  1])
        >>> r8.permute()
        >>> r8.p
        array([ 0.86,  0.08,  0.16,  0.  ,  0.02,  0.2 ,  0.56,  0.  ])

        The default is a two-sided alternative. There is an option for a
        directional alternative reflecting positive co-movement of the focal
        series with its spatial lag. In this case the number of vectors in
        quadrants I and III should be much larger than expected, while the
        counts of vectors falling in quadrants II and IV should be much lower
        than expected.

        >>> r8.permute(alternative='positive')
        >>> r8.p
        array([ 0.51,  0.04,  0.28,  0.02,  0.01,  0.14,  0.57,  0.03])

        Finally, there is a second directional alternative for examining the
        hypothesis that the focal unit and its lag move in opposite directions.

        >>> r8.permute(alternative='negative')
        >>> r8.p
        array([ 0.69,  0.99,  0.92,  1.  ,  1.  ,  0.97,  0.74,  1.  ])

        """

        self.Y = Y
        self.w = w
        self.k = k
        self.permtuations = 0
        self.sw = 2 * np.pi / self.k
        self.cuts = np.arange(0.0, 2 * np.pi + self.sw, self.sw)
        observed = self._calc(Y, w, k)
        self.theta = observed['theta']
        self.bins = observed['bins']
        self.counts = observed['counts']
        self.r = observed['r']
        self.lag = observed['lag']


    def permute(self, permutations=99, alternative='two.sided'):
        rY = self.Y.copy()
        idxs = np.arange(len(rY))
        counts = np.zeros((permutations, len(self.counts)))
        for m in range(permutations):
            np.random.shuffle(idxs)
            res = self._calc(rY[idxs,:], self.w, self.k)
            counts[m] = res['counts']
        self.counts_perm = counts
        self.larger_perm = np.array([(counts[:,i]>=self.counts[i]).sum() for i in range(self.k)])
        self.smaller_perm = np.array([(counts[:,i]<=self.counts[i]).sum() for i in range(self.k)])
        self.expected_perm = counts.mean(axis=0)
        self.std_perm = counts.std(axis=0)

        # pvalue logic
        # if P is the proportion that are as large for a one sided test (larger
        # than), then
        # p=P.
        #
        # For a two-tailed test, if P < .5, p = 2 * P, else, p = 2(1-P)
        # Source: Rayner, J. C. W., O. Thas, and D. J. Best. 2009. "Appendix B:
        # Parametric Bootstrap P-Values." In Smooth Tests of Goodness of Fit,
        # 247. John Wiley and Sons.
        # Note that the larger and smaller counts would be complements (except
        # for the shared equality, for
        # a given bin in the circular histogram. So we only need one of them.

        # We report two-sided p-values for each bin as the default
        # since a priori there could # be different alternatives for each bin depending on the problem at
        # hand.

        alt = alternative.upper()
        if alt == 'TWO.SIDED':
            P = (self.larger_perm + 1) / (permutations + 1.)
            mask = P < 0.5
            self.p = mask * 2 * P + (1 - mask) * 2 * (1-P)
        elif alt == 'POSITIVE':
            # NE, SW sectors are higher, NW, SE are lower
            POS = POS8
            if self.k == 4:
                POS = POS4
            L = (self.larger_perm + 1) / (permutations + 1.)
            S = (self.smaller_perm + 1) / (permutations + 1.)
            P = POS * L + (1-POS) * S
            self.p = P
        elif alt == 'NEGATIVE':
            # NE, SW sectors are lower, NW, SE are higher
            NEG = NEG8
            if self.k == 4:
                NEG = NEG4
            L = (self.larger_perm + 1) / (permutations + 1.)
            S = (self.smaller_perm + 1) / (permutations + 1.)
            P = NEG * L + (1-NEG) * S
            self.p = P
        else:
            print('Bad option for alternative: %s.'%alternative)


    def _calc(self, Y, w, k):
        wY = lag_spatial(w, Y)
        dx = Y[:, -1] - Y[:,0]
        dy = wY[:, -1] - wY[:, 0]
        self.wY = wY
        self.Y = Y
        r = np.sqrt(dx*dx + dy*dy)
        theta = np.arctan2(dy, dx)
        neg = theta < 0.0
        utheta = theta * (1 - neg) + neg * (2 *np.pi + theta)
        counts, bins = np.histogram(utheta, self.cuts)
        results = {}
        results['counts'] = counts
        results['theta'] = theta
        results['bins' ] = bins
        results['r'] = r
        results['lag'] = wY
        self._dx = dx
        self._dy = dy
        return results

    def plot(self, attribute=None):
        import matplotlib.cm as cm
        import matplotlib.pyplot as plt
        ax = plt.subplot(111, projection='polar')
        ax.set_rlabel_position(315)
        if attribute is None:
            c = ax.scatter(self.theta, self.r)
        else:
            c = ax.scatter(self.theta, self.r, c=attribute)
            plt.colorbar(c)

    def plot_origin(self, attribute=None):
        import matplotlib.cm as cm
        import matplotlib.pyplot as plt
        ax = plt.subplot(111 )
        xlim = [self._dx.min(), self._dx.max()]
        ylim = [self._dy.min(), self._dy.max()]
        if attribute is None:
            for x,y in zip(self._dx, self._dy):
                xs = [0, x]
                ys = [0, y]
                plt.plot(xs,ys)
            plt.axis('equal')  #<-- set the axes to the same scale
            plt.xlim(xlim) #<-- set the x axis limits
            plt.ylim(ylim) #<-- set the y axis limits


    def plot_vectors(self, attribute=None):
        import matplotlib.cm as cm
        import matplotlib.pyplot as plt
        ax = plt.subplot(111 )
        xlim = [self.Y.min(), self.Y.max()]
        ylim = [self.wY.min(), self.wY.max()]
        if attribute is None:
            for i in range(len(self.Y)):
                xs = self.Y[i,:]
                ys = self.wY[i,:]
                plt.plot(xs,ys)
            plt.axis('equal')  #<-- set the axes to the same scale
            plt.xlim(xlim) #<-- set the x axis limits
            plt.ylim(ylim) #<-- set the y axis limits
