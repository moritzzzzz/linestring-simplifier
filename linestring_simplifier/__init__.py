"""
Linestring Simplifier - Advanced geometry simplification for GeoJSON LineStrings

A Python library for intelligently simplifying linestring geometries while preserving
important geometric features like corners and curves.
"""

__version__ = "1.0.0"
__author__ = "GPX to DirectionsRoute Project"
__email__ = "contact@example.com"

from .core import SimplificationEngine
from .exceptions import (
    LinestringSimplifierError,
    InvalidGeometryError,
    InsufficientCoordinatesError
)

__all__ = [
    'SimplificationEngine',
    'LinestringSimplifierError',
    'InvalidGeometryError',
    'InsufficientCoordinatesError'
]