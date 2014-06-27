# -*- coding: utf-8 -*-
import os
from setuptools import setup

# Utility function to read the README file.  
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='CMElib',
      version='0.1.1',
      description='Symple interface for simulation of a master equation',
      author='Enrico Giampieri',
      author_email='enrico.giampieri@unibo.it',
      packages=['cmelib'],
      download_url='https://github.com/EnricoGiampieri/cmelib.git',
      url='https://github.com/EnricoGiampieri/cmelib.git',
      license = "BSD",
      long_description=read('README.md'),
      keywords = "rest API bioinformatics",
      classifiers=[
          "License :: OSI Approved :: BSD License",
          "Development Status :: 3 - Alpha",
          "Intended Audience :: Science/Research",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 2.7",
          "Topic :: Scientific/Engineering :: Bio-Informatics",
          ],
      )