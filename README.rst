GeospatIal Distribution DYnamics (giddy) in PySAL
=================================================

Giddy is an open-source python library for the analysis of dynamics of
longitudinal spatial data. Originating from the spatial dynamics module
in PySAL (Python Spatial Analysis Library), it is under active development
for the inclusion of many newly proposed analytics that consider the
role of space in the evolution of distributions over time and has
several new features including inter- and intra-regional decomposition
of mobility association and local measures of exchange mobility in
addition to space-time LISA and spatial markov methods.

.. image:: https://api.travis-ci.org/pysal/giddy.svg
   :target: https://travis-ci.org/pysal/giddy

.. image:: https://coveralls.io/repos/github/pysal/giddy/badge.svg?branch=master
   :target: https://coveralls.io/github/pysal/giddy?branch=master

.. image:: https://badges.gitter.im/pysal/giddy.svg
   :target: https://gitter.im/pysal/giddy

.. image:: https://readthedocs.org/projects/giddy/badge/?version=latest
   :target: https://giddy.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

.. image:: https://badge.fury.io/py/giddy.svg
    :target: https://badge.fury.io/py/giddy

.. image:: https://zenodo.org/badge/91390088.svg
   :target: https://zenodo.org/badge/latestdoi/91390088

.. image:: https://mybinder.org/badge_logo.svg
   :target: https://mybinder.org/v2/gh/pysal/giddy/master

This package is part of a `refactoring of PySAL
<https://github.com/pysal/pysal/wiki/PEP-13:-Refactor-PySAL-Using-Submodules>`_.

*************
Documentation
*************

Online documentation is available `here <https://giddy.readthedocs.io>`_.

*************
giddy modules
*************

- giddy.directional  Directional LISA, inference and visualization
- giddy.markov  Spatially explicit Markov methods
- giddy.mobility  Mobility indices
- giddy.rank  Spatial decomposition of exchange mobility measure

************
Installation
************

Install giddy by running:

::

    $ pip install giddy

**********
Contribute
**********

PySAL-giddy is under active development and contributors are welcome.

If you have any suggestion, feature request, or bug report, please open
a new `issue <https://github.com/pysal/giddy/issues>`__ on GitHub. To
submit patches, please follow the PySAL development
`guidelines <https://github.com/pysal/pysal/wiki>`__
and open a `pull request <https://github.com/pysal/giddy>`__. Once your
changes get merged, you’ll automatically be added to the `Contributors
List <https://github.com/pysal/giddy/graphs/contributors>`__.

*******
License
*******

The project is licensed under the `BSD
license <https://github.com/pysal/giddy/blob/master/LICENSE.txt>`__.

***************
BibTeX Citation
***************

.. code-block::
    @misc{wei_kang_2019_3251137,
      author       = {Wei Kang and
                      Sergio Rey and
                      Philip Stephens and
                      Nicholas Malizia and
                      Levi John Wolf and
                      Stefanie Lumnitz and
                      James Gaboardi and
                      jlaura and
                      Charles Schmidt and
                      eli knaap and
                      Andy Eschbacher},
      title        = {pysal/giddy: giddy 2.2.0},
      month        = jun,
      year         = 2019,
      doi          = {10.5281/zenodo.3251137},
      url          = {https://doi.org/10.5281/zenodo.3251137}
    }

*******
Funding
*******

NSF Award #1421935 `New Approaches to Spatial Distribution
Dynamics <https://www.nsf.gov/awardsearch/showAward?AWD_ID=1421935>`__


