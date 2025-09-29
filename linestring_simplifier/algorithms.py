"""
Algorithms for linestring simplification including Douglas-Peucker and corner detection.
"""

import math
from typing import List, Tuple, Set
from .geometry_utils import (
    haversine_distance, calculate_bearing, calculate_bearing_change,
    point_to_line_distance
)


class SimplificationAlgorithms:
    """Collection of algorithms for linestring simplification."""

    @staticmethod
    def douglas_peucker(coordinates: List[List[float]], tolerance: float) -> List[int]:
        """
        Apply Douglas-Peucker algorithm to find important points.

        Args:
            coordinates: List of [lon, lat] coordinate pairs
            tolerance: Distance tolerance in meters

        Returns:
            List of indices of points to keep
        """
        if len(coordinates) <= 2:
            return list(range(len(coordinates)))

        def dp_recursive(start: int, end: int) -> Set[int]:
            """Recursive helper for Douglas-Peucker."""
            if end - start <= 1:
                return {start, end}

            # Find the point with maximum distance to the line segment
            max_distance = 0
            max_index = start

            for i in range(start + 1, end):
                distance = point_to_line_distance(
                    (coordinates[i][0], coordinates[i][1]),
                    (coordinates[start][0], coordinates[start][1]),
                    (coordinates[end][0], coordinates[end][1])
                )

                if distance > max_distance:
                    max_distance = distance
                    max_index = i

            # If max distance is greater than tolerance, recursively simplify
            if max_distance > tolerance:
                left_points = dp_recursive(start, max_index)
                right_points = dp_recursive(max_index, end)
                return left_points.union(right_points)
            else:
                return {start, end}

        important_indices = dp_recursive(0, len(coordinates) - 1)
        return sorted(list(important_indices))

    @staticmethod
    def detect_corners(coordinates: List[List[float]], min_angle_change: float = 30.0) -> List[int]:
        """
        Detect corners in the linestring based on bearing changes.

        Args:
            coordinates: List of [lon, lat] coordinate pairs
            min_angle_change: Minimum angle change in degrees to consider a corner

        Returns:
            List of indices representing corner points
        """
        if len(coordinates) <= 2:
            return [0, len(coordinates) - 1]

        corners = [0]  # Always include start point

        # Look for significant bearing changes
        for i in range(1, len(coordinates) - 1):
            # Calculate bearings for segments before and after this point
            bearing_before = calculate_bearing(
                coordinates[i-1][1], coordinates[i-1][0],
                coordinates[i][1], coordinates[i][0]
            )

            bearing_after = calculate_bearing(
                coordinates[i][1], coordinates[i][0],
                coordinates[i+1][1], coordinates[i+1][0]
            )

            # Calculate the change in bearing
            bearing_change = abs(calculate_bearing_change(bearing_before, bearing_after))

            if bearing_change >= min_angle_change:
                corners.append(i)

        corners.append(len(coordinates) - 1)  # Always include end point
        return corners

    @staticmethod
    def detect_curves(coordinates: List[List[float]], window_size: int = 5,
                     curve_threshold: float = 45.0) -> List[int]:
        """
        Detect curved sections that need multiple points to represent accurately.

        Args:
            coordinates: List of [lon, lat] coordinate pairs
            window_size: Number of points to look ahead/behind for curve detection
            curve_threshold: Total bearing change threshold to consider a curve

        Returns:
            List of indices representing important points in curved sections
        """
        if len(coordinates) <= window_size * 2:
            return list(range(len(coordinates)))

        curve_points = []

        for i in range(window_size, len(coordinates) - window_size):
            # Calculate total bearing change over the window
            total_change = 0.0

            for j in range(i - window_size + 1, i + window_size):
                if j + 1 < len(coordinates):
                    bearing1 = calculate_bearing(
                        coordinates[j-1][1], coordinates[j-1][0],
                        coordinates[j][1], coordinates[j][0]
                    ) if j > 0 else 0

                    bearing2 = calculate_bearing(
                        coordinates[j][1], coordinates[j][0],
                        coordinates[j+1][1], coordinates[j+1][0]
                    )

                    if j > 0:  # Skip first point as it has no previous bearing
                        total_change += abs(calculate_bearing_change(bearing1, bearing2))

            # If total bearing change exceeds threshold, mark as curve point
            if total_change >= curve_threshold:
                curve_points.append(i)

        return curve_points

    @staticmethod
    def adaptive_simplification(coordinates: List[List[float]], max_points: int,
                               preserve_corners: bool = True,
                               preserve_curves: bool = True) -> Tuple[List[int], bool]:
        """
        Perform adaptive simplification combining multiple algorithms.

        Args:
            coordinates: List of [lon, lat] coordinate pairs
            max_points: Maximum number of points to retain
            preserve_corners: Whether to preserve detected corners
            preserve_curves: Whether to preserve curved sections

        Returns:
            Tuple of (indices_to_keep, is_sufficient) where is_sufficient indicates
            if max_points was sufficient for good representation
        """
        if len(coordinates) <= max_points:
            return list(range(len(coordinates))), True

        # Start with critical points that must be preserved
        critical_points = {0, len(coordinates) - 1}  # Always keep start and end

        # Detect and preserve corners
        if preserve_corners:
            corners = SimplificationAlgorithms.detect_corners(coordinates)
            critical_points.update(corners)

        # Detect and preserve curve points
        if preserve_curves:
            curves = SimplificationAlgorithms.detect_curves(coordinates)
            critical_points.update(curves)

        # If critical points already exceed max_points, we need to prioritize
        if len(critical_points) > max_points:
            # Keep start, end, and most important corners
            sorted_corners = SimplificationAlgorithms.detect_corners(coordinates, min_angle_change=60.0)
            critical_points = {0, len(coordinates) - 1}
            critical_points.update(sorted_corners[:max_points - 2])
            return sorted(list(critical_points)), False

        # Calculate remaining budget for Douglas-Peucker points
        remaining_budget = max_points - len(critical_points)

        if remaining_budget > 0:
            # Use Douglas-Peucker to fill remaining slots
            # Start with a high tolerance and reduce until we get enough points
            tolerance_start = 10.0  # meters
            tolerance_step = 0.5

            for tolerance in [tolerance_start * (0.8 ** i) for i in range(20)]:
                dp_points = SimplificationAlgorithms.douglas_peucker(coordinates, tolerance)

                # Combine with critical points
                all_points = critical_points.union(set(dp_points))

                if len(all_points) <= max_points:
                    # Add any remaining points from DP that fit in budget
                    additional_points = set(dp_points) - critical_points
                    points_to_add = min(remaining_budget, len(additional_points))

                    if points_to_add > 0:
                        # Sort additional points by distance from line and take the most important
                        additional_sorted = sorted(additional_points)[:points_to_add]
                        critical_points.update(additional_sorted)
                    break

        final_points = sorted(list(critical_points))
        is_sufficient = len(final_points) >= min(len(coordinates), max_points * 0.8)

        return final_points, is_sufficient