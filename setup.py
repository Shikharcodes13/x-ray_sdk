"""
Setup script for X-Ray SDK
"""
from setuptools import setup, find_packages

setup(
    name="xray-sdk",
    version="1.0.0",
    description="X-Ray execution tracking SDK",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
    ],
    python_requires=">=3.8",
)

