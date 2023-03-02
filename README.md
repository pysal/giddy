PySAL-giddy for exploratory spatiotemporal data analysis
========================================================

![Continuous Integration](https://github.com/pysal/giddy/actions/workflows/unittests.yml/badge.svg)
[![codecov](https://codecov.io/gh/pysal/giddy/branch/master/graph/badge.svg)](https://codecov.io/gh/pysal/giddy)
[![Gitter room](https://badges.gitter.im/pysal/giddy.svg)](https://gitter.im/pysal/giddy)
[![PyPI version](https://badge.fury.io/py/giddy.svg)](https://badge.fury.io/py/giddy)
[![DOI](https://zenodo.org/badge/91390088.svg)](https://zenodo.org/badge/latestdoi/91390088)
[![badge](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/pysal/giddy/master)
[![Downloads](https://static.pepy.tech/badge/giddy)](https://pepy.tech/project/giddy)

Giddy is an open-source python library for exploratory spatiotemporal data analysis and the analysis of 
geospatial distribution dynamics. 
It is under active development
for the inclusion of newly proposed analytics that consider the
role of space in the evolution of distributions over time.

*Below are six choropleth maps of U.S. state per-capita incomes from 1929 to 2004 at a fifteen-year interval.*

![us_qunitile_maps](figs/us_qunitile_maps.png)

Documentation
-------------

Online documentation is available [here](http://pysal.org/giddy/).


Features
--------
- Directional LISA, inference and visualization as rose diagram

[![rose_conditional](figs/rose_conditional.png)](notebooks/DirectionalLISA.ipynb)

*Above shows the rose diagram (directional LISAs) for US states incomes across 1969-2009 conditional on relative incomes in 1969.*

- Spatially explicit Markov methods:
    - Spatial Markov and inference
    - LISA Markov and inference
- Spatial decomposition of exchange mobility measure (rank methods):
    - Global indicator of mobility association (GIMA) and inference
    - Inter- and intra-regional decomposition of mobility association and inference
    - Local indicator of mobility association (LIMA)
        - Neighbor set LIMA and inference
        - Neighborhood set LIMA and inference

[![us_neigborsetLIMA](figs/us_neigborsetLIMA.png)](notebooks/RankBasedMethods.ipynb)

- Income mobility measures
- Alignment-based sequence analysis methods


Examples
--------

* [Directional LISA](notebooks/DirectionalLISA.ipynb)
* [Markov based methods](notebooks/MarkovBasedMethods.ipynb)
* [Rank Markov methods](notebooks/RankMarkov.ipynb)
* [Mobility measures](notebooks/MobilityMeasures.ipynb)
* [Rank based methods](notebooks/RankBasedMethods.ipynb)
* [Sequence methods (Optimal matching)](notebooks/Sequence.ipynb)

Installation
------------

Install the stable version released on the [Python Package Index](https://pypi.org/project/giddy/) from the command line:

```
pip install giddy
```

Install the development version on [pysal/giddy](https://github.com/pysal/giddy):

```
pip install https://github.com/pysal/giddy/archive/main.zip
```

#### Requirements

- scipy>=1.3.0
- libpysal>=4.0.1
- mapclassify>=2.1.1
- esda>=2.1.1
- quantecon>=0.4.7

Contribute
----------

PySAL-giddy is under active development and contributors are welcome.

If you have any suggestion, feature request, or bug report, please open a new [issue](https://github.com/pysal/giddy/issues) on GitHub. To submit patches, please follow the PySAL development [guidelines](https://github.com/pysal/pysal/wiki) and open a [pull request](https://github.com/pysal/giddy). Once your changes get merged, you’ll automatically be added to the [Contributors List](https://github.com/pysal/giddy/graphs/contributors).

Support
-------

If you are having issues, please talk to us in the [gitter room](https://gitter.im/pysal/giddy).

License
-------

The project is licensed under the [BSD license](https://github.com/pysal/giddy/blob/master/LICENSE.txt).


BibTeX Citation
---------------

```
@software{wei_kang_2020_3887455,
  author       = {Wei Kang and
                  Sergio Rey and
                  Philip Stephens and
                  Nicholas Malizia and
                  James Gaboardi and
                  Stefanie Lumnitz and
                  Levi John Wolf and
                  Charles Schmidt and
                  Jay Laura and
                  Eli Knaap},
  title        = {pysal/giddy: Release v2.3.3},
  month        = jun,
  year         = 2020,
  publisher    = {Zenodo},
  version      = {v2.3.3},
  doi          = {10.5281/zenodo.3887455},
  url          = {https://doi.org/10.5281/zenodo.3887455}
}
```

Funding
-------

<img src="figs/nsf_logo.jpg" width="50"> Award #1421935 [New Approaches to Spatial Distribution Dynamics](https://www.nsf.gov/awardsearch/showAward?AWD_ID=1421935)
