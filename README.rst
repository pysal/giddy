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

.. image:: https://img.shields.io/badge/launch-binder-579ACA.svg?logo=data:image/png;base64,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
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


