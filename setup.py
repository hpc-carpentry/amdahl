#!/usr/bin/env python

from setuptools import setup

setup(
    name="amdahl",
    version="1.0",
    python_requires=">=3",
    description="A pseudo-application that can be used as a black box to reproduce Amdahl's Law",
    author="Alan O'Cais",
    author_email="alan.ocais@cecam.org",
    url="https://github.com/ocaisa/amdahl",
    packages=["amdahl"],
    install_requires=["mpi4py"],
    entry_points={
        "console_scripts": ["amdahl=amdahl.amdahl:amdahl"],
    },
)
