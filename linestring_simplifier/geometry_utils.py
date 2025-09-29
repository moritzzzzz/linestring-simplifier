"""
Geometry utility functions for coordinate calculations and validation.
"""

import math
from typing import List, Tuple, Optional


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on the earth (specified in decimal degrees).

    Args:
        lat1, lon1: Latitude and longitude of first point
        lat2, lon2: Latitude and longitude of second point

    Returns:
        Distance in meters
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))

    # Radius of earth in meters
    r = 6371000
    return c * r


def calculate_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the bearing between two points.

    Args:
        lat1, lon1: Latitude and longitude of first point
        lat2, lon2: Latitude and longitude of second point

    Returns:
        Bearing in degrees (0-360)
    """
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    dlon = lon2 - lon1

    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(dlon))

    bearing = math.atan2(x, y)
    bearing = math.degrees(bearing)
    bearing = (bearing + 360) % 360

    return bearing


def calculate_bearing_change(bearing1: float, bearing2: float) -> float:
    """
    Calculate the change in bearing between two bearings.

    Args:
        bearing1: First bearing in degrees
        bearing2: Second bearing in degrees

    Returns:
        Bearing change in degrees (-180 to 180)
    """
    change = bearing2 - bearing1

    # Normalize to -180 to 180
    while change > 180:
        change -= 360
    while change < -180:
        change += 360

    return change


def point_to_line_distance(point: Tuple[float, float], line_start: Tuple[float, float],
                          line_end: Tuple[float, float]) -> float:
    """
    Calculate the perpendicular distance from a point to a line segment.

    Args:
        point: (lon, lat) of the point
        line_start: (lon, lat) of line start
        line_end: (lon, lat) of line end

    Returns:
        Distance in meters
    """
    # Convert to radians for accurate calculation
    px, py = math.radians(point[0]), math.radians(point[1])
    x1, y1 = math.radians(line_start[0]), math.radians(line_start[1])
    x2, y2 = math.radians(line_end[0]), math.radians(line_end[1])

    # Calculate the perpendicular distance using spherical geometry
    # This is an approximation but sufficient for our purposes

    # If line start and end are the same, return distance to that point
    if x1 == x2 and y1 == y2:
        return haversine_distance(
            math.degrees(py), math.degrees(px),
            math.degrees(y1), math.degrees(x1)
        )

    # Calculate cross-track distance (approximation for small distances)
    bearing_line = math.atan2(math.sin(x2-x1) * math.cos(y2),
                             math.cos(y1) * math.sin(y2) - math.sin(y1) * math.cos(y2) * math.cos(x2-x1))

    bearing_point = math.atan2(math.sin(px-x1) * math.cos(py),
                              math.cos(y1) * math.sin(py) - math.sin(y1) * math.cos(py) * math.cos(px-x1))

    distance_to_start = haversine_distance(
        math.degrees(y1), math.degrees(x1),
        math.degrees(py), math.degrees(px)
    )

    cross_track_distance = math.asin(math.sin(distance_to_start / 6371000) *
                                    math.sin(bearing_point - bearing_line)) * 6371000

    return abs(cross_track_distance)


def validate_geojson_linestring(geometry: dict) -> bool:
    """
    Validate that a geometry object is a proper GeoJSON LineString.

    Args:
        geometry: Dictionary representing a GeoJSON geometry

    Returns:
        True if valid, False otherwise
    """
    if not isinstance(geometry, dict):
        return False

    if geometry.get('type') != 'LineString':
        return False

    coordinates = geometry.get('coordinates', [])
    if not isinstance(coordinates, list) or len(coordinates) < 2:
        return False

    # Check that all coordinates are valid [lon, lat] pairs
    for coord in coordinates:
        if not isinstance(coord, list) or len(coord) < 2:
            return False
        if not all(isinstance(x, (int, float)) for x in coord[:2]):
            return False
        # Basic longitude/latitude bounds check
        lon, lat = coord[0], coord[1]
        if not (-180 <= lon <= 180) or not (-90 <= lat <= 90):
            return False

    return True


def calculate_linestring_length(coordinates: List[List[float]]) -> float:
    """
    Calculate the total length of a linestring in meters.

    Args:
        coordinates: List of [lon, lat] coordinate pairs

    Returns:
        Total length in meters
    """
    if len(coordinates) < 2:
        return 0.0

    total_length = 0.0
    for i in range(len(coordinates) - 1):
        lon1, lat1 = coordinates[i][0], coordinates[i][1]
        lon2, lat2 = coordinates[i + 1][0], coordinates[i + 1][1]
        total_length += haversine_distance(lat1, lon1, lat2, lon2)

    return total_length