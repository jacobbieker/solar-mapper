#!/usr/bin/env python
from pathlib import Path

from setuptools import find_packages, setup

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()
install_requires = (this_directory / "requirements.txt").read_text().splitlines()


setup(
    name="solar_mapper",
    version="0.0.2",
    description="Global Solar Mapping with Satellite Imagery",
    author="Jacob Bieker",
    author_email="jacob@bieker.tech",
    url="https://github.com/jacobbieker/solar-mapper",  # REPLACE WITH YOUR OWN GITHUB PROJECT LINK
    install_requires=install_requires,
    long_description=long_description,
    include_package_data=True,
    packages=find_packages(),
)
