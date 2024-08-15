.. Installation

Installation
============

giddy currently supports python `3.10`_, `3.11`_, and `3.12`_.
Please make sure that you are operating in a python 3 environment.

Installing released version
---------------------------

giddy is available on the `Python Package Index`_. Therefore, you can either
install directly with `pip` from the command line::

  pip install -U giddy


or download the source distribution (.tar.gz) and decompress it to your selected
destination. Open a command shell and navigate to the decompressed folder.
Type::

  pip install .

You may also install the latest stable giddy via `conda-forge`_ channel by
running::

  conda install --channel conda-forge giddy

Installing development version
------------------------------

Potentially, you might want to use the newest features in the development
version of giddy on github - `pysal/giddy`_ while have not been incorporated
in the Pypi released version. You can achieve that by installing `pysal/giddy`_
by running the following from a command shell::

  pip install git+https://github.com/pysal/giddy.git

You can  also `fork`_ the `pysal/giddy`_ repo and create a local clone of
your fork. By making changes
to your local clone and submitting a pull request to `pysal/giddy`_, you can
contribute to the giddy development.

.. _3.10: https://docs.python.org/3.10/
.. _3.11: https://docs.python.org/3.11/
.. _3.12: https://docs.python.org/3.12/
.. _Python Package Index: https://pypi.org/project/giddy/
.. _pysal/giddy: https://github.com/pysal/giddy
.. _fork: https://help.github.com/articles/fork-a-repo/
.. _conda-forge: https://github.com/conda-forge/giddy-feedstock
