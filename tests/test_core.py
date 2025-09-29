"""
Unit tests for the linestring_simplifier core functionality.
"""

import unittest
import json
from linestring_simplifier import (
    SimplificationEngine,
    InvalidGeometryError,
    InsufficientCoordinatesError
)


class TestSimplificationEngine(unittest.TestCase):
    """Test cases for SimplificationEngine."""

    def setUp(self):
        """Set up test fixtures."""
        self.engine = SimplificationEngine()

        # Test linestring - a simple route with some turns
        self.test_linestring = {
            "type": "LineString",
            "coordinates": [
                [-122.4194, 37.7749],  # Start
                [-122.4194, 37.7849],  # North
                [-122.4094, 37.7849],  # East (corner)
                [-122.4094, 37.7949],  # North
                [-122.3994, 37.7949],  # East (corner)
                [-122.3994, 37.8049],  # North
                [-122.3894, 37.8049],  # East (corner)
                [-122.3894, 37.8149],  # End
            ]
        }

    def test_basic_simplification(self):
        """Test basic simplification functionality."""
        result = self.engine.simplify_linestring(
            geojson_geometry=self.test_linestring,
            max_coordinates=5
        )

        self.assertIsInstance(result, dict)
        self.assertIn('geometry', result)
        self.assertIn('original_count', result)
        self.assertIn('simplified_count', result)
        self.assertEqual(result['original_count'], 8)
        self.assertLessEqual(result['simplified_count'], 5)
        self.assertEqual(result['geometry']['type'], 'LineString')

    def test_no_simplification_needed(self):
        """Test case where no simplification is needed."""
        result = self.engine.simplify_linestring(
            geojson_geometry=self.test_linestring,
            max_coordinates=10
        )

        self.assertEqual(result['simplified_count'], result['original_count'])
        self.assertEqual(result['reduction_ratio'], 0.0)
        self.assertTrue(result['was_sufficient'])

    def test_json_string_input(self):
        """Test with JSON string input."""
        json_string = json.dumps(self.test_linestring)
        result = self.engine.simplify_linestring(
            geojson_geometry=json_string,
            max_coordinates=5
        )

        self.assertIsInstance(result, dict)
        self.assertEqual(result['original_count'], 8)

    def test_invalid_geometry(self):
        """Test with invalid geometry."""
        invalid_geometry = {
            "type": "Point",
            "coordinates": [-122.4194, 37.7749]
        }

        with self.assertRaises(InvalidGeometryError):
            self.engine.simplify_linestring(invalid_geometry, 5)

    def test_invalid_json_string(self):
        """Test with invalid JSON string."""
        with self.assertRaises(InvalidGeometryError):
            self.engine.simplify_linestring("invalid json", 5)

    def test_insufficient_coordinates(self):
        """Test with insufficient coordinate limit."""
        with self.assertRaises(InsufficientCoordinatesError) as context:
            self.engine.simplify_linestring(self.test_linestring, 1)

        self.assertIsInstance(context.exception.minimum_required, int)
        self.assertEqual(context.exception.provided_limit, 1)

    def test_geometry_validation(self):
        """Test geometry validation method."""
        result = self.engine.validate_geometry(self.test_linestring)

        self.assertTrue(result['is_valid'])
        self.assertEqual(result['geometry_type'], 'LineString')
        self.assertEqual(result['coordinate_count'], 8)
        self.assertGreater(result['total_length'], 0)
        self.assertGreaterEqual(result['minimum_coordinates_required'], 2)

    def test_simplification_preview(self):
        """Test simplification preview functionality."""
        result = self.engine.get_simplification_preview(
            geojson_geometry=self.test_linestring,
            max_coordinates_options=[3, 5, 8, 10]
        )

        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 4)

        # Test that 10 coordinates shows no error (no simplification needed)
        self.assertNotIn('error', result[10])

        # Test that very low coordinate count may show error
        if 'error' in result[3]:
            self.assertIn('error_type', result[3])

    def test_corner_preservation(self):
        """Test that corners are properly preserved."""
        result = self.engine.simplify_linestring(
            geojson_geometry=self.test_linestring,
            max_coordinates=5,
            preserve_corners=True
        )

        # Should preserve start, end, and most significant corners
        self.assertGreaterEqual(result['simplified_count'], 3)

        coords = result['geometry']['coordinates']
        # First and last should be preserved
        self.assertEqual(coords[0], self.test_linestring['coordinates'][0])
        self.assertEqual(coords[-1], self.test_linestring['coordinates'][-1])

    def test_curve_preservation(self):
        """Test curve preservation functionality."""
        # Create a curved linestring
        curved_linestring = {
            "type": "LineString",
            "coordinates": [
                [-122.4194, 37.7749],
                [-122.4184, 37.7759],
                [-122.4174, 37.7769],
                [-122.4164, 37.7779],
                [-122.4154, 37.7789],  # Gradual curve
                [-122.4144, 37.7799],
                [-122.4134, 37.7809],
                [-122.4124, 37.7819],
            ]
        }

        result = self.engine.simplify_linestring(
            geojson_geometry=curved_linestring,
            max_coordinates=4,
            preserve_curves=True
        )

        self.assertLessEqual(result['simplified_count'], 4)
        self.assertGreaterEqual(result['length_preserved'], 80.0)  # Should preserve most of the length


class TestGeometryUtils(unittest.TestCase):
    """Test geometry utility functions."""

    def setUp(self):
        self.engine = SimplificationEngine()

    def test_empty_linestring(self):
        """Test handling of empty linestring."""
        empty_linestring = {
            "type": "LineString",
            "coordinates": []
        }

        result = self.engine.validate_geometry(empty_linestring)
        self.assertFalse(result['is_valid'])

    def test_single_point_linestring(self):
        """Test handling of single point linestring."""
        single_point = {
            "type": "LineString",
            "coordinates": [[-122.4194, 37.7749]]
        }

        result = self.engine.validate_geometry(single_point)
        self.assertFalse(result['is_valid'])

    def test_two_point_linestring(self):
        """Test handling of minimal valid linestring."""
        two_points = {
            "type": "LineString",
            "coordinates": [
                [-122.4194, 37.7749],
                [-122.4094, 37.7849]
            ]
        }

        result = self.engine.simplify_linestring(two_points, 10)
        self.assertEqual(result['simplified_count'], 2)
        self.assertTrue(result['was_sufficient'])


if __name__ == '__main__':
    unittest.main()