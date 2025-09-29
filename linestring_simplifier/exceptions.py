"""
Custom exceptions for the linestring_simplifier library.
"""


class LinestringSimplifierError(Exception):
    """Base exception for all linestring simplifier errors."""
    pass


class InvalidGeometryError(LinestringSimplifierError):
    """Raised when input geometry is invalid or unsupported."""
    pass


class InsufficientCoordinatesError(LinestringSimplifierError):
    """Raised when the maximum coordinate limit is insufficient to represent the geometry properly."""

    def __init__(self, message, minimum_required=None, provided_limit=None):
        super().__init__(message)
        self.minimum_required = minimum_required
        self.provided_limit = provided_limit