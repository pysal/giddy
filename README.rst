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

.. image:: https://badge.fury.io/py/pypi.svg
    :target: https://badge.fury.io/py/pypi

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.2633309.svg
   :target: https://doi.org/10.5281/zenodo.2633309

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
`guidelines <http://pysal.readthedocs.io/en/latest/developers/index.html>`__
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
    @misc{giddy_2019_2633309,
      author       = {Wei Kang and
                      Sergio Rey and
                      Philip Stephens and
                      Nicholas Malizia and
                      Levi John Wolf and
                      Stefanie Lumnitz and
                      jlaura and
                      Charles Schmidt and
                      eli knaap and
                      James Gaboardi and
                      Andy Eschbacher},
      title        = {pysal/giddy: giddy 2.1.0},
      month        = apr,
      year         = 2019,
      doi          = {10.5281/zenodo.2633309},
      url          = {https://doi.org/10.5281/zenodo.2633309}
    }

*******
Funding
*******

NSF Award #1421935 `New Approaches to Spatial Distribution
Dynamics <https://www.nsf.gov/awardsearch/showAward?AWD_ID=1421935>`__


