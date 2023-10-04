import numpy as np
import pytest
from ..sequence import Sequence
import libpysal
import mapclassify as mc


def test_Sequence_unequal():
    """
    1. Testing on sequences of unequal lengths.
    """

    seq1 = "ACGGTAG"
    seq2 = "CCTAAG"
    seq3 = "CCTAAGC"

    # 1.1 substitution cost matrix and indel cost are not given, and will be
    # generated based on the distance type "interval"
    seqAna = Sequence([seq1, seq2, seq3], dist_type="interval")
    subs_mat = np.array(
        [
            [0.0, 1.0, 2.0, 3.0],
            [1.0, 0.0, 1.0, 2.0],
            [2.0, 1.0, 0.0, 1.0],
            [3.0, 2.0, 1.0, 0.0],
        ]
    )
    seq_dis_mat = np.array([[0.0, 7.0, 10.0], [7.0, 0.0, 3.0], [10.0, 3.0, 0.0]])
    assert seqAna.k == 4
    np.testing.assert_allclose(seqAna.subs_mat, subs_mat)
    np.testing.assert_allclose(seqAna.seq_dis_mat, seq_dis_mat)

    # 1.2 User-defined substitution cost matrix and indel cost
    subs_mat = np.array(
        [
            [0, 0.76, 0.29, 0.05],
            [0.30, 0, 0.40, 0.60],
            [0.16, 0.61, 0, 0.26],
            [0.38, 0.20, 0.12, 0],
        ]
    )
    indel = subs_mat.max()
    seqAna = Sequence([seq1, seq2, seq3], subs_mat=subs_mat, indel=indel)
    seq_dis_mat = np.array([[0.0, 1.94, 2.46], [1.94, 0.0, 0.76], [2.46, 0.76, 0.0]])
    np.testing.assert_allclose(seqAna.seq_dis_mat, seq_dis_mat)
    # 1.3 Calculating "hamming" distance will fail on unequal sequences

    with pytest.raises(
        ValueError,
    ):
        Sequence([seq1, seq2, seq3], dist_type="hamming")


def test_Sequence_equal():
    """
    2. Testing on sequences of equal length.
    """

    seq1 = "ACGGTAG"
    seq2 = "CCTAAGA"
    seq3 = "CCTAAGC"

    # 2.1 Calculating "hamming" distance will not fail on equal sequences

    seqAna = Sequence([seq1, seq2, seq3], dist_type="hamming")
    seq_dis_mat = np.array([[0.0, 6.0, 6.0], [6.0, 0.0, 1.0], [6.0, 1.0, 0.0]])
    np.testing.assert_allclose(seqAna.seq_dis_mat, seq_dis_mat)

    # 2.2 User-defined substitution cost matrix and indel cost (distance
    #     between different types is always 1 and indel cost is 2 or larger) -
    #     give the same sequence distance matrix as "hamming" distance
    subs_mat = np.array(
        [
            [0.0, 1.0, 1.0, 1.0],
            [1.0, 0.0, 1.0, 1.0],
            [1.0, 1.0, 0.0, 1.0],
            [1.0, 1.0, 1.0, 0.0],
        ]
    )
    indel = 2
    seqAna = Sequence([seq1, seq2, seq3], subs_mat=subs_mat, indel=indel)
    seq_dis_mat = np.array([[0.0, 6.0, 6.0], [6.0, 0.0, 1.0], [6.0, 1.0, 0.0]])
    np.testing.assert_allclose(seqAna.seq_dis_mat, seq_dis_mat)

    # 2.3 User-defined substitution cost matrix and indel cost (distance
    #     between different types is always 1 and indel cost is 1) - give a
    #     slightly different sequence distance matrix from "hamming" distance since
    #     insertion and deletion is happening
    indel = 1
    seqAna = Sequence([seq1, seq2, seq3], subs_mat=subs_mat, indel=indel)
    seq_dis_mat = np.array([[0.0, 5.0, 5.0], [5.0, 0.0, 1.0], [5.0, 1.0, 0.0]])
    np.testing.assert_allclose(seqAna.seq_dis_mat, seq_dis_mat)

    f = libpysal.io.open(libpysal.examples.get_path("usjoin.csv"))
    pci = np.array([f.by_col[str(y)] for y in range(1929, 2010)])
    q5 = np.array([mc.Quantiles(y, k=5).yb for y in pci]).transpose()
    seqs = q5[:5, :]  # only look at the first 5 sequences

    # "hamming"
    seq_hamming = Sequence(seqs, dist_type="hamming")
    seq_dis_mat = np.array(
        [
            [0.0, 75.0, 7.0, 81.0, 81.0],
            [75.0, 0.0, 80.0, 81.0, 65.0],
            [7.0, 80.0, 0.0, 81.0, 81.0],
            [81.0, 81.0, 81.0, 0.0, 69.0],
            [81.0, 65.0, 81.0, 69.0, 0.0],
        ]
    )
    np.testing.assert_allclose(seq_hamming.seq_dis_mat, seq_dis_mat)

    # "interval"
    seq_interval = Sequence(seqs, dist_type="interval")
    seq_dis_mat = np.array(
        [
            [0.0, 123.0, 7.0, 308.0, 230.0],
            [123.0, 0.0, 130.0, 185.0, 109.0],
            [7.0, 130.0, 0.0, 315.0, 237.0],
            [308.0, 185.0, 315.0, 0.0, 90.0],
            [230.0, 109.0, 237.0, 90.0, 0.0],
        ]
    )
    np.testing.assert_allclose(seq_interval.seq_dis_mat, seq_dis_mat)

    # "arbitrary"
    seq_arbitrary = Sequence(seqs, dist_type="arbitrary")
    seq_dis_mat = np.array(
        [
            [0.0, 37.5, 3.5, 40.5, 40.5],
            [37.5, 0.0, 40.0, 40.5, 32.5],
            [3.5, 40.0, 0.0, 40.5, 40.5],
            [40.5, 40.5, 40.5, 0.0, 34.5],
            [40.5, 32.5, 40.5, 34.5, 0.0],
        ]
    )
    np.testing.assert_allclose(seq_arbitrary.seq_dis_mat, seq_dis_mat)

    # "markov"
    seq_markov = Sequence(seqs, dist_type="markov")
    seq_dis_mat = np.array(
        [
            [0.0, 72.69026039, 6.44797042, 81.0, 81.0],
            [72.69026039, 0.0, 77.55529756, 80.91834743, 58.93609228],
            [6.44797042, 77.55529756, 0.0, 81.0, 81.0],
            [81.0, 80.91834743, 81.0, 0.0, 63.14216005],
            [81.0, 58.93609228, 81.0, 63.14216005, 0.0],
        ]
    )
    np.testing.assert_allclose(seq_markov.seq_dis_mat, seq_dis_mat)

    # "tran"
    seq_tran = Sequence(seqs, dist_type="tran")
    seq_dis_mat = np.array(
        [
            [0.0, 23.0, 8.0, 10.0, 30.0],
            [23.0, 0.0, 17.0, 20.0, 33.0],
            [8.0, 17.0, 0.0, 6.0, 24.0],
            [10.0, 20.0, 6.0, 0.0, 27.0],
            [30.0, 33.0, 24.0, 27.0, 0.0],
        ]
    )
    np.testing.assert_allclose(seq_tran.seq_dis_mat, seq_dis_mat)
