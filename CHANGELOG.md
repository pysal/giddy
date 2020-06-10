# Version 2.3.3 (2020-06-10)

This release does not add new functionalities for spatiotemporal analytics. Instead, it features the additional support of python 3.8 and the migration of the documentation website host from readthedocs to GitHub Page. The new docs website is http://pysal.org/giddy. 

In addition, two GitHub workflows for (1) [continuous integration](https://github.com/pysal/giddy/actions?query=workflow%3A%22Continuous+Integration%22) and (2) [building and releasing the package to pypi and github](https://github.com/pysal/giddy/actions?query=workflow%3A%22Build%2C+Release%2C+and+publish%22) are configured to automate these maintenance process with GitHub Actions.

We closed a total of 65 issues (enhancements and bug fixes) through 30 pull requests, since our last release on 2019-12-20. (A complete history of release details is reported in [CHANGELOG.md](https://github.com/pysal/giddy/blob/master/CHANGELOG.md)).

## Issues Closed
  - version bump to v2.3.3 (#158)
  - (bug) pytest-runner is deprecated (#157)
  - Prepare for releasing v2.3.2 as v2.3.1 is broken (#156)
  - Follow-up fixes for the automatic release of v2.3.1 with github actions (#155)
  - Prepare for a formal release of giddy v2.3.1 with GitHub actions (#154)
  - fix for github actions release (name of changelog) (#153)
  - GitHub actions (packing and releasing) - pack the updated changelog to the built distribution (#152)
  - Fixes for building and releasing with github actions (#151)
  - (bug) fix workflow of building and releasing  (#150)
  - Name of the passwords are capitalized (#149)
  - Version bump for building and releasing with GitHub actions (testing) (#148)
  - Give a name to the continuous testing workflow (#147)
  - (bug) fix workflow of GitHub actions for building and releasing a package (#146)
  - release and publish with github actions (#145)
  - CI only testing against master branch (#143)
  - Update README (#144)
  - badges for CI with github actions and codecov (#141)
  - migrate from readthedocs to github page for docs hosting (#142)
  - fix docs (with nbsphinx) (#140)
  - Continuous integration using GitHub Actions (#139)
  - add requirements on quantecon (>=0.4.7) (#138)
  - code formatting with black (#137)
  - spatial_dynamics.interaction migration? (#124)
  - remove accidentally added testing notebook (#136)
  - Binder for examples is missing dependencies (#132)
  - (bug) adding missing dependencies for Binder  (#135)
  - output for classic Markov needs slight rewording (#133)
  - rewording summary output for Markov chains (#134)
  - (bug) sojourn_time for p with rows of 0s (#131)
  - Links broken with https://github.com/pysal/giddy/tutorial (#129)
  - fix for #129 (#130)
  - github page redirected to readthedocs page (#128)
  - Extend functions for Markov classes to deal with non-ergodic Markov chains (#107)
  - prepare for releasing V2.3.0 (#127)
  - (ENH) Extend functions for Markov classes to deal with non-ergodic Markov chains (#109)

## Pull Requests
  - version bump to v2.3.3 (#158)
  - (bug) pytest-runner is deprecated (#157)
  - Prepare for releasing v2.3.2 as v2.3.1 is broken (#156)
  - Follow-up fixes for the automatic release of v2.3.1 with github actions (#155)
  - Prepare for a formal release of giddy v2.3.1 with GitHub actions (#154)
  - fix for github actions release (name of changelog) (#153)
  - GitHub actions (packing and releasing) - pack the updated changelog to the built distribution (#152)
  - Fixes for building and releasing with github actions (#151)
  - (bug) fix workflow of building and releasing  (#150)
  - Name of the passwords are capitalized (#149)
  - Version bump for building and releasing with GitHub actions (testing) (#148)
  - Give a name to the continuous testing workflow (#147)
  - (bug) fix workflow of GitHub actions for building and releasing a package (#146)
  - release and publish with github actions (#145)
  - CI only testing against master branch (#143)
  - Update README (#144)
  - badges for CI with github actions and codecov (#141)
  - migrate from readthedocs to github page for docs hosting (#142)
  - fix docs (with nbsphinx) (#140)
  - Continuous integration using GitHub Actions (#139)
  - add requirements on quantecon (>=0.4.7) (#138)
  - code formatting with black (#137)
  - remove accidentally added testing notebook (#136)
  - (bug) adding missing dependencies for Binder  (#135)
  - rewording summary output for Markov chains (#134)
  - (bug) sojourn_time for p with rows of 0s (#131)
  - fix for #129 (#130)
  - github page redirected to readthedocs page (#128)
  - prepare for releasing V2.3.0 (#127)
  - (ENH) Extend functions for Markov classes to deal with non-ergodic Markov chains (#109)

The following individuals contributed to this release:

  - Wei Kang
  - Serge Rey
  - James Gaboardi
  
# Version 2.3.0 (2019-12-20)

We closed a total of 11 issues (enhancements and bug fixes) through 5 pull requests, since our last release on 2019-09-06.

## Issues Closed
  - (ENH) Extend functions for Markov classes to deal with non-ergodic Markov chains (#109)
  - travis CI: pip install from git clone (#126)
  - rewrite utility function "get_lower" using numpy's more efficient functionality (#125)
  - Release version 2.2.2 for bug fix  (#121)
  - prepare for new release: version 2.2.2  (#123)
  - remove the parameter in plt.show() due to the API change in Matplotlib (deprecation) (#122)

## Pull Requests
  - (ENH) Extend functions for Markov classes to deal with non-ergodic Markov chains (#109)
  - travis CI: pip install from git clone (#126)
  - rewrite utility function "get_lower" using numpy's more efficient functionality (#125)
  - prepare for new release: version 2.2.2  (#123)
  - remove the parameter in plt.show() due to the API change in Matplotlib (deprecation) (#122)

The following individuals contributed to this release:

  - Wei Kang
  - James Gaboardi

# Version 2.2.2 (2019-09-06)

We closed a total of 21 issues (enhancements and bug fixes) through 9 pull requests, since our last release on 2019-07-25.

## Issues Closed
  - remove the parameter in plt.show() due to the API change in Matplotlib (deprecation) (#122)
  - development guidelines link in README.md (#119)
  - BUG: Fix for correct handling of ties in Tau (#118)
  - resolving broken dev link (#120)
  - initialization of ECount parameter in Kendall's Tau (#117)
  - (bug) debug travis-ci  (#116)
  - docs building is failing (#114)
  - (docs, bug) fix docs building and configure nbsphinx to work with binder in docs tutorials (#115)
  -  (docs) rename notebooks for configuring nbsphinx and binder (#113)
  - docs updates for v2.2.1 (#112)
  - update dependency versions (#111)
  - Prepare for new release 2.2.1 which will have the addition of sequence methods (#110)

## Pull Requests
  - remove the parameter in plt.show() due to the API change in Matplotlib (deprecation) (#122)
  - BUG: Fix for correct handling of ties in Tau (#118)
  - resolving broken dev link (#120)
  - (bug) debug travis-ci  (#116)
  - (docs, bug) fix docs building and configure nbsphinx to work with binder in docs tutorials (#115)
  -  (docs) rename notebooks for configuring nbsphinx and binder (#113)
  - docs updates for v2.2.1 (#112)
  - update dependency versions (#111)
  - Prepare for new release 2.2.1 which will have the addition of sequence methods (#110)

The following individuals contributed to this release:

  - Wei Kang
  - James Gaboardi
  - Serge Rey
  
# Version 2.2.1 (2019-07-25)

We closed a total of 21 issues (enhancements and bug fixes) through 10 pull requests, since our last release on 2019-06-20.

## Issues Closed
  - Prepare for new release 2.2.1 which will have the addition of sequence methods (#110)
  - Is it good practice to reuse a function name as the name of a class attribute? (#108)
  - (Docs) add tutorial page (#106)
  - (docs)  add zenodo citation to docs landing page (#105)
  - update Readme for v2.2.0 (#104)
  - edits on OM variant of transitions (#103)
  - (ENH) Sequence methods (#101)
  - (docs) reference label style (#102)
  - (bug) setup.py: md as long description (#100)
  - Prepare for release 2.2.0 (#99)

## Pull Requests
  - Prepare for new release 2.2.1 which will have the addition of sequence methods (#110)
  - (Docs) add tutorial page (#106)
  - (docs)  add zenodo citation to docs landing page (#105)
  - update Readme for v2.2.0 (#104)
  - edits on OM variant of transitions (#103)
  - (ENH) Sequence methods (#101)
  - (docs) reference label style (#102)
  - (bug) setup.py: md as long description (#100)
  - Prepare for release 2.2.0 (#99)

The following individuals contributed to this release:

  - Wei Kang
  - Serge Rey
  
# Version 2.2.0 (2019-06-20)

We closed a total of 25 issues (enhancements and bug fixes) through 11 pull requests, since our last release on 2019-04-08.

## Issues Closed
  - (docs) update installation instructions (#98)
  - (docs) change the css to accommodate new versions of sphinx and sphinx bootstrap theme  (#97)
  - PyPi page configuration (#96)
  - pip install github master.zip of pysal dependencies (#95)
  - update README.md (#93)
  - Update readme (#94)
  - migrate from readthedocs configuration file v1 to v2 (#92)
  - updating supported python versions (3.6 and 3.7) in setup.py (#91)
  - Move testing off of 3.5 and add 3.7 (#90)
  - release on conda-forge (#89)
  - allow user specified lag and check shape (#53)
  - Update zenodo doi and pypi badge for version 2.1.0 (new release) (#87)
  - (bug) format readme.rst as long_description for pypi display (#86)
  - Prepare for release 2.1.0 (#85)

## Pull Requests
  - (docs) update installation instructions (#98)
  - (docs) change the css to accommodate new versions of sphinx and sphinx bootstrap theme  (#97)
  - PyPi page configuration (#96)
  - pip install github master.zip of pysal dependencies (#95)
  - Update readme (#94)
  - migrate from readthedocs configuration file v1 to v2 (#92)
  - updating supported python versions (3.6 and 3.7) in setup.py (#91)
  - Move testing off of 3.5 and add 3.7 (#90)
  - Update zenodo doi and pypi badge for version 2.1.0 (new release) (#87)
  - (bug) format readme.rst as long_description for pypi display (#86)
  - Prepare for release 2.1.0 (#85)

The following individuals contributed to this release:

  - Wei Kang
  - James Gaboardi
  
# Version 2.1.0 (2019-04-08)

We closed a total of 36 issues (enhancements and bug fixes) through 16 pull requests, since our last release on 2018-08-26.

## Issues Closed
  - Add splot as a soft dependency for giddy  (#84)
  - .travis built on archaic Miniconda (#82)
  - explicitly specifying Miniconda3 in .travis.yml (#83)
  - configure doctest and coverage testing (#81)
  - remove plot directive and indents (#80)
  - reference labels are missing from rendered docs (#77)
  - fix missing reference labels in rendered docs  (#79)
  - (ENH) Full rank and geographic rank Markov methods (#73)
  - (BUG) update directional notebook to accommodate changes in libpysal (#78)
  - (BUG) fix notebooks (#76)
  - remove redundant installation in travis.yml (#75)
  - add pypi badge to README (#74)
  - (BUG) remove libpysal.api in Rank notebook (#72)
  - update required versions of dependencies (#71)
  - Update issue templates (#70)
  - conform to PEP8 style guide (#69)
  - Singular matrix when computing ergodic values (#32)
  - build notebooks for documentation (#6)
  - update README with new doi and doc website (#68)
  - REL: 2.0.0 (#67)

## Pull Requests
  - Add splot as a soft dependency for giddy  (#84)
  - explicitly specifying Miniconda3 in .travis.yml (#83)
  - configure doctest and coverage testing (#81)
  - remove plot directive and indents (#80)
  - fix missing reference labels in rendered docs  (#79)
  - (ENH) Full rank and geographic rank Markov methods (#73)
  - (BUG) update directional notebook to accommodate changes in libpysal (#78)
  - (BUG) fix notebooks (#76)
  - remove redundant installation in travis.yml (#75)
  - add pypi badge to README (#74)
  - (BUG) remove libpysal.api in Rank notebook (#72)
  - update required versions of dependencies (#71)
  - Update issue templates (#70)
  - conform to PEP8 style guide (#69)
  - update README with new doi and doc website (#68)
  - REL: 2.0.0 (#67)

The following individuals contributed to this release:

  - Wei Kang
  - James Gaboardi
  - Serge Rey
  
# Version 2.0.0 (2018-08-26)

This release does not add any new functionality to `giddy`, but
instead features api changes in `giddy` and its
pysal submodule dependencies `mapclassify`, `libpysal`, and `esda`. More
specifically, the `giddy.api` module which was originally designed to
 facilitate a smoother transition from the old metapackage pysal to the
 refactored submodule structure (see [here](http://pysal.org/about.html#migrating-to-pysal-2-0)
 for details) was removed as we are moving away from the
refactoring stage and looking at the future development.

We closed a total of 20 issues (enhancements and bug fixes) through 9 pull requests, since our last release on 2018-07-27.

## Issues Closed
  - remove giddy.api in README.rst (#66)
  -  chore: update for libpysal lower case module name changes (#65)
  - remove api.py (#62)
  - set up travis dual testing against mapclassify and  esda (#63)
  - replace `libpysal.api` imports with new imports in `markov.py` and `d… (#61)
  - Remove api.py and account for changes in (incoming) API of mapclassify, esda, and libpysal (#64)
  - version giddy only in giddy/__ini__.py (#60)
  - remove duplicate makefile for sphinx build (#59)
  - add zenodo doi badge to README (#58)
  - add changelog for the release 1.2.0 (#57)
  - prepare for release 1.2.0 (#56)

## Pull Requests
  - remove giddy.api in README.rst (#66)
  -  chore: update for libpysal lower case module name changes (#65)
  - replace `libpysal.api` imports with new imports in `markov.py` and `d… (#61)
  - Remove api.py and account for changes in (incoming) API of mapclassify, esda, and libpysal (#64)
  - version giddy only in giddy/__ini__.py (#60)
  - remove duplicate makefile for sphinx build (#59)
  - add zenodo doi badge to README (#58)
  - add changelog for the release 1.2.0 (#57)
  - prepare for release 1.2.0 (#56)

The following individuals contributed to this release:

  - Wei Kang
  - Stefanie Lumnitz

# Version 1.2.0 (2018-07-27)

This release features:
* a more flexible specification for the [spatial Markov chains model](https://github.com/pysal/giddy/blob/master/giddy/markov.py#L169).More specifically, for continuous time series input:
    * both the numbers of classifications for input continuous time series (k) and spatial lags (m) can be specified and allowed to be different
    * user-defined classifications (cutoffs) for input continuous time series and spatial lags are allowed
* new visualization tools:
    * relies on [pysal/splot](https://github.com/pysal/splot) for [visualizing
    Dynamic LISA related statistics](https://github.com/pysal/giddy/blob/master/giddy/directional.py#L322)
* launch of the [documentation website](http://giddy.readthedocs.io/)

GitHub stats for 2018/05/18 - 2018/07/27

These lists are automatically generated, and may be incomplete or contain duplicates.

We closed a total of 34 issues, 16 pull requests and 18 regular issues;
this is the full list (generated with the script
:file:`tools/github_stats.py`):

## Pull Requests (16):

* :ghpull:`56`: b'prepare for release 1.2.0'
* :ghpull:`55`: b'set up dual travis tests for libpysal (pip and github)'
* :ghpull:`54`: b'ENH: Allow for more flexible specification of Spatial Markov'
* :ghpull:`52`: b'Update notebooks to rely on geopandas for mapping'
* :ghpull:`51`: b'ENH to docs'
* :ghpull:`50`: b'include /tests in the release and correct for the directional doctests'
* :ghpull:`49`: b'add doc building badge to README'
* :ghpull:`47`: b'Tests and documentation for `rose.plot()` and `rose.plot_vectors()`'
* :ghpull:`48`: b'A tentative version of giddy documentation website with sphinx '
* :ghpull:`46`: b'force utf8 for the install description read'
* :ghpull:`43`: b'implement `rose.plot()` and `rose.plot_vectors()` method using `splot`'
* :ghpull:`44`: b'More on building doc webpages using sphinx'
* :ghpull:`42`: b'Gallery'
* :ghpull:`41`: b'new features for sphinx documentation website'
* :ghpull:`40`: b'typo - email notifications'
* :ghpull:`38`: b'fix for python 3'

## Issues (18):

* :ghissue:`56`: b'prepare for release 1.2.0'
* :ghissue:`55`: b'set up dual travis tests for libpysal (pip and github)'
* :ghissue:`54`: b'ENH: Allow for more flexible specification of Spatial Markov'
* :ghissue:`52`: b'Update notebooks to rely on geopandas for mapping'
* :ghissue:`51`: b'ENH to docs'
* :ghissue:`50`: b'include /tests in the release and correct for the directional doctests'
* :ghissue:`49`: b'add doc building badge to README'
* :ghissue:`47`: b'Tests and documentation for `rose.plot()` and `rose.plot_vectors()`'
* :ghissue:`48`: b'A tentative version of giddy documentation website with sphinx '
* :ghissue:`45`: b'encoding issue in  README.rst'
* :ghissue:`46`: b'force utf8 for the install description read'
* :ghissue:`43`: b'implement `rose.plot()` and `rose.plot_vectors()` method using `splot`'
* :ghissue:`44`: b'More on building doc webpages using sphinx'
* :ghissue:`42`: b'Gallery'
* :ghissue:`41`: b'new features for sphinx documentation website'
* :ghissue:`40`: b'typo - email notifications'
* :ghissue:`38`: b'fix for python 3'
* :ghissue:`39`: b'first draft of sphinx gallery'

# Version 1.1.1 (2018-05-17)

This release is the first tagged release of giddy on Github.
Starting from this release, giddy supports python 3.5 and 3.6 only.
This release also features categorical spatial Markov which enables spatial Markov
(class [Spatial_Markov](https://github.com/pysal/giddy/blob/master/giddy/markov.py#L179))
to be applied to categorical time series such as land use and land cover change,
as well as neighborhood change. Here, the spatial lag (utilizing function
[lag_categorical](https://github.com/pysal/libpysal/blob/master/libpysal/weights/spatial_lag.py#L88)
in [libpysal](https://github.com/pysal/libpysal)) is defined as the most
common category among neighbors.

GitHub stats for 2017/07/21 - 2018/05/17

These lists are automatically generated, and may be incomplete or contain duplicates.


We closed a total of 20 issues, 8 pull requests and 12 regular issues;
this is the full list (generated with the script 
:file:`tools/github_stats.py`):

## Pull Requests (8):

* :ghpull:`36`: b'add changelog for the release 1.1.0'
* :ghpull:`35`: b'prepare for release'
* :ghpull:`34`: b'code 2to3'
* :ghpull:`33`: b'chore: update for python 3+ only'
* :ghpull:`28`: b'add inequality to api'
* :ghpull:`29`: b'adding discretized Spatial_Markov'
* :ghpull:`25`: b'[WIP] prepare for full metapackage integration'
* :ghpull:`27`: b'api module for giddy'

## Issues (12):

* :ghissue:`36`: b'add changelog for the release 1.1.0'
* :ghissue:`35`: b'prepare for release'
* :ghissue:`34`: b'code 2to3'
* :ghissue:`33`: b'chore: update for python 3+ only'
* :ghissue:`31`: b"How to use the 'development' version"
* :ghissue:`30`: b'KeyError: 1 in spatial_lag.py'
* :ghissue:`26`: b'giddy needs an api.py module'
* :ghissue:`28`: b'add inequality to api'
* :ghissue:`29`: b'adding discretized Spatial_Markov'
* :ghissue:`25`: b'[WIP] prepare for full metapackage integration'
* :ghissue:`27`: b'api module for giddy'
* :ghissue:`12`: b'Publish on PyPi'
