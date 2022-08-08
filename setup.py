#!/usr/bin/env python

import os

from setuptools import setup


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="amdahl",
    version="0.3.1",
    author="Alan O'Cais",
    author_email="alan.ocais@cecam.org",
    python_requires=">=3",
    description="A pseudo-application that can be used as a black box to reproduce Amdahl's Law",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ocaisa/amdahl",
    packages=["amdahl"],
    install_requires=["mpi4py"],
    entry_points={
        "console_scripts": ["amdahl = amdahl.amdahl:amdahl"],
    },
)
