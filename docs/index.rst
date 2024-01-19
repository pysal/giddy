.. giddy documentation master file, created by
   sphinx-quickstart on Wed Jun  6 15:54:22 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

GeospatIal Distribution DYnamics (GIDDY)
========================================

Giddy is an open-source python library for the analysis of dynamics of
longitudinal spatial data. Originating from the spatial dynamics module
in `PySAL`_ (Python Spatial Analysis Library), it is under active development
for the inclusion of many newly proposed analytics that consider the
role of space in the evolution of distributions over time and has
several new features including inter- and intra-regional decomposition
of mobility association and local measures of exchange mobility in
addition to space-time LISA and spatial markov methods.


.. raw:: html

    <div class="container-fluid">
      <div class="row equal-height">
        <div class="col-sm-1 col-xs-hidden">
        </div>
        <div class="col-md-3 col-xs-12">
            <a href="http://nbviewer.jupyter.org/github/pysal/giddy/blob/main/notebooks/DirectionalLISA.ipynb" class="thumbnail">
                <img src="_static/images/rose_conditional.png" class="img-responsive center-block">
                <div class="caption text-center">
                <h6>Rose diagram (directional LISAs)</h6>
                </div>
            </a>
        </div>
        <div class="col-sm-3 col-xs-12">
            <a href="http://nbviewer.jupyter.org/github/pysal/giddy/blob/main/notebooks/MarkovBasedMethods.ipynb" class="thumbnail">
                <img src="_static/images/spatial_markov_us.png" class="img-responsive center-block">
                <div class="caption text-center">
                <h6>Spatial Markov Chain</h6>
                </div>
            </a>
        </div>
        <div class="col-sm-3 col-xs-12">
            <a href="http://nbviewer.jupyter.org/github/pysal/giddy/blob/main/notebooks/RankBasedMethods.ipynb" class="thumbnail">
                <img src="_static/images/neighboorsetLIMA_US.png"
                class="img-responsive center-block">
                <div class="caption text-center">
                <h6>Neighbor Set Local Indicator of Mobility Association (LIMA)
                </h6>
                </div>
            </a>
        </div>
        <div class="col-sm-2 col-xs-hidden">
        </div>
      </div>
    </div>

Citing `giddy`
--------------

If you use PySAL-giddy in a scientific publication, we would appreciate using the following citation:

Bibtex entry::

   @software{wei_kang_2024_10520458,
     author       = {Wei Kang and
                     Sergio Rey and
                     James Gaboardi and
                     Philip Stephens and
                     Nicholas Malizia and
                     Stefanie Lumnitz and
                     Levi John Wolf and
                     Charles Schmidt and
                     Jay Laura and
                     eli knaap},
     title        = {pysal/giddy: v2.3.5},
     month        = jan,
     year         = 2024,
     publisher    = {Zenodo},
     version      = {v2.3.5},
     doi          = {10.5281/zenodo.10520458},
     url          = {https://doi.org/10.5281/zenodo.10520458}
   }

.. toctree::
   :hidden:
   :maxdepth: 3
   :caption: Contents:

   Installation <installation>
   Tutorial <tutorial>
   API <api>
   References <references>



.. _PySAL: https://github.com/pysal/pysal