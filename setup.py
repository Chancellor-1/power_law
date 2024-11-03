""" Module containing the project setup, used for installation. """
# Copyright (C) 2024 Chancellor - License GPLv3
from pathlib import Path
from setuptools import setup, find_packages

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='pow-law',
    version='1.0.3',
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/Chancellor-1/power_law',
    author='Chancellor',
    author_email='chancelloratbrinkofbailout@gmail.com',
    description='This Python tool can visualize e.g. the Bitcoin and Kaspa price together with their power law price channels.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[
        'matplotlib>=3.5.0',
        'coinapi.rest.v1>=1.3',
        'pyyaml>=6.0',
        'scikit-learn>=1.0, <1.4',
        'zipp>=3.20',
        'ipykernel>=6.1.0'
    ],
    python_requires='>=3.8.2, <3.13',
    entry_points={
        'console_scripts': [
            'pow-law=power_law.__main__:main'
        ]
    }
)
