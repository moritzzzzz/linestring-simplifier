# Linestring Simplifier

Advanced geometry simplification for GeoJSON LineStrings with intelligent corner and curve preservation.

## Features

- **Smart Simplification**: Combines Douglas-Peucker algorithm with corner detection and curve preservation
-  **Coordinate Budgeting**: Respects maximum coordinate limits while preserving essential geometry
️- **Intelligent Warnings**: Provides feedback when coordinate limits are insufficient
-  **Detailed Metrics**: Returns simplification statistics and geometry analysis 
- **Zero Dependencies**: Uses only Python standard library for maximum compatibility

## Installation

```bash
pip install linestring-simplifier
```

## Quick Start

```python
from linestring_simplifier import SimplificationEngine

# Create engine
engine = SimplificationEngine()

# Example GeoJSON LineString
linestring = {
    "type": "LineString",
    "coordinates": [
        [-122.4194, 37.7749],
        [-122.4094, 37.7849],
        [-122.3994, 37.7949],
        # ... many more coordinates
    ]
}

# Simplify to maximum 50 coordinates
result = engine.simplify_linestring(
    geojson_geometry=linestring,
    max_coordinates=50
)

print(f"Reduced from {result['original_count']} to {result['simplified_count']} coordinates")
print(f"Length preserved: {result['length_preserved']:.1f}%")

simplified_geometry = result['geometry']
```

## Advanced Usage

### Corner and Curve Preservation

```python
# Customize preservation settings
result = engine.simplify_linestring(
    geojson_geometry=linestring,
    max_coordinates=50,
    preserve_corners=True,           # Detect and preserve corners
    preserve_curves=True,            # Preserve curved sections
    min_angle_for_corners=30.0,      # Minimum angle change for corners (degrees)
    curve_detection_threshold=45.0   # Total bearing change threshold for curves
)
```

### Geometry Validation and Analysis

```python
# Validate and analyze geometry
analysis = engine.validate_geometry(linestring)

print(f"Geometry is valid: {analysis['is_valid']}")
print(f"Total length: {analysis['total_length']:.2f} meters")
print(f"Minimum coordinates required: {analysis['minimum_coordinates_required']}")
print(f"Detected corners: {analysis['detected_corners']}")
print(f"Complexity score: {analysis['complexity_score']:.3f}")
```

### Preview Different Coordinate Limits

```python
# Test multiple coordinate limits
preview = engine.get_simplification_preview(
    geojson_geometry=linestring,
    max_coordinates_options=[10, 25, 50, 100]
)

for limit, stats in preview.items():
    if 'error' not in stats:
        print(f"{limit} coords: {stats['simplified_count']} used, "
              f"{stats['length_preserved']:.1f}% length preserved")
```

## Error Handling

```python
from linestring_simplifier import InsufficientCoordinatesError, InvalidGeometryError

try:
    result = engine.simplify_linestring(linestring, max_coordinates=5)
except InsufficientCoordinatesError as e:
    print(f"Need at least {e.minimum_required} coordinates (you provided {e.provided_limit})")
except InvalidGeometryError as e:
    print(f"Invalid geometry: {e}")
```

## Algorithm Details

### Hybrid Approach

The simplifier uses a multi-step approach:

1. **Corner Detection**: Identifies significant direction changes based on bearing analysis
2. **Curve Detection**: Finds curved sections that need multiple points for accurate representation
3. **Critical Point Preservation**: Ensures important geometric features are never removed
4. **Douglas-Peucker Fill**: Uses remaining coordinate budget for optimal point selection
5. **Quality Validation**: Checks if the result adequately represents the original geometry

### Smart Coordinate Budgeting

When coordinate limits are tight, the algorithm:

- Prioritizes start/end points (always preserved)
- Preserves the most significant corners first
- Allocates remaining coordinates using Douglas-Peucker
- Warns when limits are insufficient for good representation

## Return Value Details

The `simplify_linestring()` method returns a dictionary with:

```python
{
    'geometry': {},           # Simplified GeoJSON LineString
    'original_count': 150,    # Original coordinate count
    'simplified_count': 50,   # Simplified coordinate count
    'reduction_ratio': 66.7,  # Percentage reduction
    'length_preserved': 98.5, # Percentage of original length preserved
    'warnings': [],           # List of warning messages
    'was_sufficient': True    # Whether max_coordinates was sufficient
}
```

## Performance

- **Memory efficient**: Processes coordinates in-place where possible
- **Fast execution**: Optimized algorithms with minimal overhead
- **Scalable**: Handles linestrings from small routes to large GPS tracks

## Use Cases

- **Map Matching APIs**: Reduce coordinate count for API limits (e.g., Mapbox 100-coordinate limit)
- **Data Storage**: Minimize storage requirements while preserving geometry
- **Visualization**: Optimize geometries for web mapping applications
- **GPS Track Processing**: Simplify recorded tracks while preserving route characteristics

## Contributing

Please feel free to submit pull requests or open issues.

## License

MIT License - see LICENSE file for details.
