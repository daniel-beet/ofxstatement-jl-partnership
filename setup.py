#!/usr/bin/python3
"""Setup
"""
from setuptools import find_packages
from distutils.core import setup

version = "0.0.1"

with open('README.rst') as f:
    long_description = f.read()

setup(name='ofxstatement-jl-partnership',
      version=version,
      author="Daniel Beet",
      author_email="dan@ionicblue.com",
      url="https://github.com/ionicblue/ofxstatement-jl-partnership",
      description=("OFXStatement plugin for John Lewis Partnership card (UK)"),
      long_description=long_description,
      license="MIT",
      keywords=["ofx", "banking", "statement", "john lewis", "partnership"],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Programming Language :: Python :: 3',
          'Natural Language :: English',
          'Topic :: Office/Business :: Financial :: Accounting',
          'Topic :: Utilities',
          'Environment :: Console',
          'Operating System :: OS Independent',
          'License :: OSI Approved :: GNU Affero General Public License v3'],
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=["ofxstatement", "ofxstatement.plugins"],
      entry_points={
          'ofxstatement':
          ['jlpartnership = ofxstatement.plugins.jlpartnership:JLPartnershipPlugin']
          },
      install_requires=['ofxstatement'],
      include_package_data=True,
      zip_safe=True
      )
