"""
Core SimplificationEngine class for linestring simplification.
"""

import json
import copy
import warnings
from typing import Dict, Any, List, Optional, Union

from .exceptions import (
    InvalidGeometryError,
    InsufficientCoordinatesError
)
from .geometry_utils import (
    validate_geojson_linestring,
    calculate_linestring_length
)
from .algorithms import SimplificationAlgorithms


class SimplificationEngine:
    """
    Main engine for intelligently simplifying GeoJSON LineString geometries.

    This class provides advanced simplification capabilities that preserve important
    geometric features like corners and curves while respecting coordinate limits.
    """

    def __init__(self):
        """Initialize the SimplificationEngine."""
        self.algorithms = SimplificationAlgorithms()

    def simplify_linestring(
        self,
        geojson_geometry: Union[Dict[str, Any], str],
        max_coordinates: int,
        preserve_corners: bool = True,
        preserve_curves: bool = True,
        min_angle_for_corners: float = 30.0,
        curve_detection_threshold: float = 45.0
    ) -> Dict[str, Any]:
        """
        Simplify a GeoJSON LineString geometry to a maximum number of coordinates.

        Args:
            geojson_geometry: GeoJSON LineString geometry as dict or JSON string
            max_coordinates: Maximum number of coordinates to retain
            preserve_corners: Whether to preserve detected corners
            preserve_curves: Whether to preserve curved sections
            min_angle_for_corners: Minimum angle change (degrees) to detect corners
            curve_detection_threshold: Total bearing change threshold for curve detection

        Returns:
            Dict containing:
                - 'geometry': Simplified GeoJSON LineString geometry
                - 'original_count': Number of original coordinates
                - 'simplified_count': Number of coordinates after simplification
                - 'reduction_ratio': Percentage of coordinates removed
                - 'length_preserved': Percentage of original length preserved
                - 'warnings': List of any warnings generated
                - 'was_sufficient': Whether max_coordinates was sufficient for good representation

        Raises:
            InvalidGeometryError: If input geometry is invalid
            InsufficientCoordinatesError: If max_coordinates is too low for minimum representation
        """
        # Parse input geometry
        if isinstance(geojson_geometry, str):
            try:
                geometry = json.loads(geojson_geometry)
            except json.JSONDecodeError as e:
                raise InvalidGeometryError(f"Invalid JSON string: {e}")
        else:
            geometry = copy.deepcopy(geojson_geometry)

        # Validate geometry
        if not validate_geojson_linestring(geometry):
            raise InvalidGeometryError("Input must be a valid GeoJSON LineString geometry")

        coordinates = geometry['coordinates']
        original_count = len(coordinates)

        # Handle edge cases
        if max_coordinates < 2:
            raise InsufficientCoordinatesError(
                "max_coordinates must be at least 2 for a valid LineString",
                minimum_required=2,
                provided_limit=max_coordinates
            )

        if original_count <= max_coordinates:
            # No simplification needed
            return {
                'geometry': geometry,
                'original_count': original_count,
                'simplified_count': original_count,
                'reduction_ratio': 0.0,
                'length_preserved': 100.0,
                'warnings': [],
                'was_sufficient': True
            }

        # Calculate original length
        original_length = calculate_linestring_length(coordinates)

        # Perform adaptive simplification
        indices_to_keep, was_sufficient = self.algorithms.adaptive_simplification(
            coordinates=coordinates,
            max_points=max_coordinates,
            preserve_corners=preserve_corners,
            preserve_curves=preserve_curves
        )

        # Create simplified geometry
        simplified_coordinates = [coordinates[i] for i in indices_to_keep]
        simplified_geometry = {
            'type': 'LineString',
            'coordinates': simplified_coordinates
        }

        # Calculate metrics
        simplified_count = len(simplified_coordinates)
        reduction_ratio = ((original_count - simplified_count) / original_count) * 100
        simplified_length = calculate_linestring_length(simplified_coordinates)
        length_preserved = (simplified_length / original_length * 100) if original_length > 0 else 100.0

        # Generate warnings
        warnings_list = []
        if not was_sufficient:
            warnings_list.append(
                f"The specified max_coordinates ({max_coordinates}) may be insufficient "
                f"to properly represent this geometry. Consider increasing the limit."
            )

        if simplified_count < max_coordinates * 0.5:
            warnings_list.append(
                f"Simplified geometry uses only {simplified_count} of {max_coordinates} "
                f"allowed coordinates. The original geometry may be very simple."
            )

        if length_preserved < 95.0:
            warnings_list.append(
                f"Length preservation is {length_preserved:.1f}%. "
                f"Consider increasing max_coordinates for better accuracy."
            )

        # Check if we need to raise InsufficientCoordinatesError
        minimum_required = self._calculate_minimum_required(coordinates)
        if max_coordinates < minimum_required:
            raise InsufficientCoordinatesError(
                f"Cannot represent this geometry with only {max_coordinates} coordinates. "
                f"Minimum required: {minimum_required}",
                minimum_required=minimum_required,
                provided_limit=max_coordinates
            )

        return {
            'geometry': simplified_geometry,
            'original_count': original_count,
            'simplified_count': simplified_count,
            'reduction_ratio': reduction_ratio,
            'length_preserved': length_preserved,
            'warnings': warnings_list,
            'was_sufficient': was_sufficient
        }

    def _calculate_minimum_required(self, coordinates: List[List[float]]) -> int:
        """
        Calculate the minimum number of coordinates required to represent the geometry.

        This is based on detecting essential corners and the start/end points.

        Args:
            coordinates: List of [lon, lat] coordinate pairs

        Returns:
            Minimum number of coordinates required
        """
        if len(coordinates) <= 2:
            return len(coordinates)

        # Find essential corners (large angle changes)
        essential_corners = self.algorithms.detect_corners(coordinates, min_angle_change=90.0)

        # Always need at least start and end
        minimum = max(3, len(essential_corners))

        # Add some buffer for curves between corners
        return min(minimum + 2, len(coordinates))

    def get_simplification_preview(
        self,
        geojson_geometry: Union[Dict[str, Any], str],
        max_coordinates_options: List[int]
    ) -> Dict[int, Dict[str, Any]]:
        """
        Preview simplification results for different coordinate limits.

        Args:
            geojson_geometry: GeoJSON LineString geometry as dict or JSON string
            max_coordinates_options: List of different coordinate limits to test

        Returns:
            Dictionary mapping each coordinate limit to its simplification results
        """
        results = {}

        for limit in max_coordinates_options:
            try:
                result = self.simplify_linestring(geojson_geometry, limit)
                results[limit] = {
                    'simplified_count': result['simplified_count'],
                    'reduction_ratio': result['reduction_ratio'],
                    'length_preserved': result['length_preserved'],
                    'was_sufficient': result['was_sufficient'],
                    'warning_count': len(result['warnings'])
                }
            except (InvalidGeometryError, InsufficientCoordinatesError) as e:
                results[limit] = {
                    'error': str(e),
                    'error_type': type(e).__name__
                }

        return results

    def validate_geometry(self, geojson_geometry: Union[Dict[str, Any], str]) -> Dict[str, Any]:
        """
        Validate a GeoJSON LineString geometry and return analysis.

        Args:
            geojson_geometry: GeoJSON LineString geometry as dict or JSON string

        Returns:
            Dictionary containing validation results and geometry analysis
        """
        # Parse input
        if isinstance(geojson_geometry, str):
            try:
                geometry = json.loads(geojson_geometry)
            except json.JSONDecodeError as e:
                return {
                    'is_valid': False,
                    'error': f"Invalid JSON: {e}",
                    'geometry_type': None,
                    'coordinate_count': 0,
                    'total_length': 0.0
                }
        else:
            geometry = geojson_geometry

        # Validate
        is_valid = validate_geojson_linestring(geometry)

        if not is_valid:
            return {
                'is_valid': False,
                'error': "Invalid GeoJSON LineString geometry",
                'geometry_type': geometry.get('type'),
                'coordinate_count': 0,
                'total_length': 0.0
            }

        # Analyze geometry
        coordinates = geometry['coordinates']
        coordinate_count = len(coordinates)
        total_length = calculate_linestring_length(coordinates)
        minimum_required = self._calculate_minimum_required(coordinates)

        corners = self.algorithms.detect_corners(coordinates)
        curves = self.algorithms.detect_curves(coordinates)

        return {
            'is_valid': True,
            'error': None,
            'geometry_type': 'LineString',
            'coordinate_count': coordinate_count,
            'total_length': total_length,
            'minimum_coordinates_required': minimum_required,
            'detected_corners': len(corners),
            'detected_curves': len(curves),
            'complexity_score': (len(corners) + len(curves)) / coordinate_count if coordinate_count > 0 else 0
        }