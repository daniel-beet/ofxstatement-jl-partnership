#!/usr/bin/python3
"""Setup
"""
from distutils.core import setup

from setuptools import find_packages

version = "1.0.0"

with open("README.rst") as f:
    long_description = f.read()

setup(
    name="ofxstatement-jl-partnership",
    version=version,
    author="Daniel Beet",
    author_email="dan@ionicblue.com",
    url="https://github.com/daniel-beet/ofxstatement-jl-partnership",
    description=("OFXStatement plugin for John Lewis Partnership card (UK)"),
    long_description=long_description,
    license="MIT",
    keywords=["ofx", "banking", "statement", "john lewis", "partnership"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
        "Natural Language :: English",
        "Topic :: Office/Business :: Financial :: Accounting",
        "Topic :: Utilities",
        "Environment :: Console",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
    packages=find_packages("src"),
    package_dir={"": "src"},
    namespace_packages=["ofxstatement", "ofxstatement.plugins"],
    entry_points={
        "ofxstatement": [
            "jlpartnership = ofxstatement.plugins.jlpartnership:JLPartnershipPlugin"
        ]
    },
    install_requires=["ofxstatement"],
    include_package_data=True,
    zip_safe=True,
)
