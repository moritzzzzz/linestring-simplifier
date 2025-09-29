"""
Setup configuration for linestring_simplifier package.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Advanced geometry simplification for GeoJSON LineStrings"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="linestring-simplifier",
    version="1.0.0",
    author="Moritz Foerster",
    author_email="mo@moses-ai.com",
    description="Advanced geometry simplification for GeoJSON LineStrings with corner and curve preservation",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/example/linestring-simplifier",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: GIS",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    keywords="gis geojson linestring simplification douglas-peucker geometry",
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "test": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "linestring-simplifier=linestring_simplifier.cli:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/moritzzzzz/linestring-simplifier/issues",
        "Source": "https://github.com/moritzzzzz/linestring-simplifier",
        "Documentation": "https://github.com/moritzzzzz/linestring-simplifier",
    },
    include_package_data=True,
    zip_safe=False,

)
