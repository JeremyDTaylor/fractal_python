#!/usr/bin/env python

"""The setup script."""

from setuptools import find_packages, setup

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = [
    "requests>=2.25.1",
    "attrs>=20.3.0",
    "deserialize>=1.8.0",
    "arrow>=1.0.0",
    "stringcase>=1.2.0",
]

setup_requirements = [
    "pytest-runner",
]

test_requirements = [
    "pytest>=6",
    "pytest-mock>=3.5.1",
    "requests-mock>=1.7.0",
    "pytest-freezegun>=0.4.2",
]

setup(
    author="Jeremy David Taylor",
    author_email="jeremy@tab2.com",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    description="Python SDK for Fractal Labs API",
    install_requires=requirements,
    license="Apache Software License 2.0",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="fractal_python",
    name="fractal_python",
    packages=find_packages(include=["fractal_python", "fractal_python.*"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/JeremyDTaylor/fractal_python",
    version="0.1.0",
    zip_safe=False,
)
