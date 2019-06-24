import unittest
import numpy as np
import pytest
from ..sequence import Sequence
import libpysal
import mapclassify as mc

def test_Sequence_unequal():
    '''
    1. Testing on sequences of unequal lengths.
    '''

    seq1 = 'ACGGTAG'
    seq2 = 'CCTAAG'
    seq3 = 'CCTAAGC'

    # 1.1 substitution cost matrix and indel cost are not given, and will be
    # generated based on the distance type "interval"
    seqAna = Sequence([seq1, seq2, seq3], dist_type="interval")
    subs_mat = np.array([[0., 1., 2., 3.],
                         [1., 0., 1., 2.],
                         [2., 1., 0., 1.],
                         [3., 2., 1., 0.]])
    seq_dis_mat = np.array([[ 0.,  7., 10.],
                            [ 7.,  0.,  3.],
                            [10.,  3.,  0.]])
    assert seqAna.k == 4
    np.testing.assert_allclose(seqAna.subs_mat, subs_mat)
    np.testing.assert_allclose(seqAna.seq_dis_mat, seq_dis_mat)


    # 1.2 User-defined substitution cost matrix and indel cost
    subs_mat = np.array([[0, 0.76, 0.29, 0.05],
                         [0.30, 0, 0.40, 0.60],
                         [0.16, 0.61, 0, 0.26],
                         [0.38, 0.20, 0.12, 0]])
    indel = subs_mat.max()
    seqAna = Sequence([seq1, seq2, seq3], subs_mat=subs_mat, indel=indel)
    seq_dis_mat = np.array([[0.  , 1.94, 2.46],
                            [1.94, 0.  , 0.76],
                            [2.46, 0.76, 0.  ]])
    np.testing.assert_allclose(seqAna.seq_dis_mat, seq_dis_mat)
    # 1.3 Calculating "hamming" distance will fail on unequal sequences

    with pytest.raises(ValueError,):
        Sequence([seq1, seq2, seq3], dist_type="hamming")


def test_Sequence_equal():
    '''
    2. Testing on sequences of equal length.
    '''

    seq1 = 'ACGGTAG'
    seq2 = 'CCTAAGA'
    seq3 = 'CCTAAGC'

    # 2.1 Calculating "hamming" distance will not fail on equal sequences

    seqAna = Sequence([seq1, seq2, seq3], dist_type="hamming")
    seq_dis_mat = np.array([[0., 6., 6.],
                            [6., 0., 1.],
                            [6., 1., 0.]])
    np.testing.assert_allclose(seqAna.seq_dis_mat, seq_dis_mat)

    # 2.2 User-defined substitution cost matrix and indel cost (distance
    #     between different types is always 1 and indel cost is 2 or larger) -
    #     give the same sequence distance matrix as "hamming" distance
    subs_mat = np.array([[0., 1., 1., 1.], [1., 0., 1., 1.], [1., 1., 0., 1.],
                         [1., 1., 1., 0.]])
    indel = 2
    seqAna = Sequence([seq1, seq2, seq3], subs_mat=subs_mat, indel=indel)
    seq_dis_mat = np.array([[0., 6., 6.],[6., 0., 1.],[6., 1., 0.]])
    np.testing.assert_allclose(seqAna.seq_dis_mat, seq_dis_mat)

    # 2.3 User-defined substitution cost matrix and indel cost (distance
    #     between different types is always 1 and indel cost is 1) - give a
    #     slightly different sequence distance matrix from "hamming" distance since
    #     insertion and deletion is happening
    indel = 1
    seqAna = Sequence([seq1, seq2, seq3], subs_mat=subs_mat, indel=indel)
    seq_dis_mat = np.array([[0., 5., 5.],[5., 0., 1.],[5., 1., 0.]])
    np.testing.assert_allclose(seqAna.seq_dis_mat, seq_dis_mat)

    f = libpysal.io.open(libpysal.examples.get_path("usjoin.csv"))
    pci = np.array([f.by_col[str(y)] for y in range(1929, 2010)])
    q5 = np.array([mc.Quantiles(y, k=5).yb for y in pci]).transpose()
    seqs = q5[:5, :] #only look at the first 5 sequences

    #"hamming"
    seq_hamming = Sequence(seqs, dist_type="hamming")
    seq_dis_mat = np.array([[ 0., 75.,  7., 81., 81.],
                            [75.,  0., 80., 81., 65.],
                            [ 7., 80.,  0., 81., 81.],
                            [81., 81., 81.,  0., 69.],
                            [81., 65., 81., 69.,  0.]])
    np.testing.assert_allclose(seq_hamming.seq_dis_mat, seq_dis_mat)

    #"interval"
    seq_interval = Sequence(seqs, dist_type="interval")
    seq_dis_mat = np.array([[  0., 123.,   7., 308., 230.],
                            [123.,   0., 130., 185., 109.],
                            [  7., 130.,   0., 315., 237.],
                            [308., 185., 315.,   0.,  90.],
                            [230., 109., 237.,  90.,   0.]])
    np.testing.assert_allclose(seq_interval.seq_dis_mat, seq_dis_mat)

    #"arbitrary"
    seq_arbitrary = Sequence(seqs, dist_type="arbitrary")
    seq_dis_mat = np.array([[ 0. , 37.5,  3.5, 40.5, 40.5],
                            [37.5,  0. , 40. , 40.5, 32.5],
                            [ 3.5, 40. ,  0. , 40.5, 40.5],
                            [40.5, 40.5, 40.5,  0. , 34.5],
                            [40.5, 32.5, 40.5, 34.5,  0. ]])
    np.testing.assert_allclose(seq_arbitrary.seq_dis_mat, seq_dis_mat)

    # "markov"
    seq_markov = Sequence(seqs, dist_type="markov")
    seq_dis_mat = np.array([[ 0.        , 72.69026039,  6.44797042, 81.        , 81.        ],
                            [72.69026039,  0.        , 77.55529756, 80.91834743, 58.93609228],
                            [ 6.44797042, 77.55529756,  0.        , 81.        , 81.        ],
                            [81., 80.91834743, 81., 0., 63.14216005],
                            [81.        , 58.93609228, 81.        , 63.14216005,  0.        ]])
    np.testing.assert_allclose(seq_markov.seq_dis_mat, seq_dis_mat)

    # "tran"
    seq_tran = Sequence(seqs, dist_type="tran")
    seq_dis_mat = np.array([[ 0., 23.,  8., 10., 30.],
                            [23.,  0., 17., 20., 33.],
                            [ 8., 17.,  0.,  6., 24.],
                            [10., 20.,  6.,  0., 27.],
                            [30., 33., 24., 27.,  0.]])
    np.testing.assert_allclose(seq_tran.seq_dis_mat, seq_dis_mat)

