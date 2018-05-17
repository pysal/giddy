"""GIDDY: GeospatIal Distribution DYnamics

Giddy is an open-source python library for the analysis of dynamics of
longitudinal spatial data. Originating from the spatial dynamics module
in PySAL (Python Spatial Analysis Library), it is under active development
for the inclusion of many newly proposed analytics that consider the
role of space in the evolution of distributions over time and has
several new features including inter- and intra-regional decomposition
of mobility association and local measures of exchange mobility in
addition to space-time LISA and spatial markov methods. Give
giddy a try if you are interested in space-time analysis!

"""

DOCLINES = __doc__.split("\n")

with open('README.rst') as file:
    long_description = file.read()


from setuptools import setup
from distutils.command.build_py import build_py

Major = 1
Feature = 1
Bug = 1
VERSION = '%d.%d.%d' % (Major, Feature, Bug)

def setup_package():
    setup(name='giddy',  # name of package
          version=VERSION,
          description=DOCLINES[0],
          #long_description="\n".join(DOCLINES[2:]),
          long_description = long_description,
          url='https://github.com/pysal/giddy',
          maintainer='Wei Kang',
          maintainer_email='weikang9009@gmail.com',
          py_modules=['giddy'],
          python_requires='>3.4',
          test_suite='nose.collector',
          tests_require=['nose'],
          keywords='spatial statistics, spatiotemporal analysis',
          classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Science/Research',
            'Intended Audience :: Developers',
            'Intended Audience :: Education',
            'Topic :: Scientific/Engineering',
            'Topic :: Scientific/Engineering :: GIS',
            'License :: OSI Approved :: BSD License',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6'
            ],
          license='3-Clause BSD',
          packages=['giddy'],
          install_requires=['libpysal', 'mapclassify', 'esda'],
          zip_safe=False,
          cmdclass={'build.py': build_py})

if __name__ == '__main__':
    setup_package()