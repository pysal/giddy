.. _api_ref:

.. currentmodule:: giddy

API reference
=============

.. _markov_api:

Markov Methods
--------------

.. autosummary::
   :toctree: generated/

    giddy.markov.Markov
    giddy.markov.Spatial_Markov
    giddy.markov.LISA_Markov
    giddy.markov.FullRank_Markov
    giddy.markov.GeoRank_Markov
    giddy.markov.kullback
    giddy.markov.prais
    giddy.markov.homogeneity
    giddy.markov.sojourn_time
    giddy.ergodic.steady_state
    giddy.ergodic.fmpt
    giddy.ergodic.var_fmpt


.. _directional_api:

Directional LISA
----------------

.. autosummary::
   :toctree: generated/

    giddy.directional.Rose


.. _mobility_api:

Economic Mobility Indices
-------------------------
.. autosummary::
   :toctree: generated/

    giddy.mobility.markov_mobility

.. _rank_api:

Exchange Mobility Methods
-------------------------
.. autosummary::
   :toctree: generated/

    giddy.rank.Theta
    giddy.rank.Tau
    giddy.rank.SpatialTau
    giddy.rank.Tau_Local
    giddy.rank.Tau_Local_Neighbor
    giddy.rank.Tau_Local_Neighborhood
    giddy.rank.Tau_Regional

.. _sequence_api:
Alignment-based Sequence Methods
--------------------------------

.. autosummary::
   :toctree: generated/

    giddy.sequence.Sequence

.. _utility_api:
Utility Functions
-----------------

.. autosummary::
   :toctree: generated/

    giddy.util.shuffle_matrix
    giddy.util.get_lower
    giddy.util.fill_empty_diagonals
