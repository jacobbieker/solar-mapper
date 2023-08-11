#!/usr/bin/env python

from setuptools import find_packages, setup

setup(
    name="solar_mapper",
    version="0.0.1",
    description="Global Solar Mapping with Satellite Imagery",
    author="Jacob Bieker",
    author_email="jacob@bieker.tech",
    url="https://github.com/jacobbieker/solar-mapper",  # REPLACE WITH YOUR OWN GITHUB PROJECT LINK
    install_requires=["pytorch-lightning", "hydra-core"],
    packages=find_packages(),
)
