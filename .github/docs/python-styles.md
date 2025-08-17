# Code Style & Formatting

- **Follow PEP 8** style guidelines strictly
- Use **4 spaces** for indentation (no tabs)
- Maximum line length of **88 characters** (Black formatter standard)
- Use **double quotes** for strings unless single quotes avoid escaping
- Import organization: standard library → third-party → local imports
- Do not use wildcard imports (e.g., `from module import *`)
- Avoid unnecessary complexity in code structure
- Do not use spaces in empty lines. Empty lines should be completely blank.

# Type Hints & Documentation

- **Always use type hints** for function parameters and return values
- Use `from __future__ import annotations` for forward references
- Include **docstrings** for all public functions, classes, and modules using Google style format:

```python
def calculate_area(radius: float) -> float:
    """Calculate the area of a circle.

    Args:
        radius: The radius of the circle in meters.

    Returns:
        The area of the circle in square meters.

    Raises:
        ValueError: If radius is negative.
    """
    if radius < 0:
        raise ValueError("Radius must be non-negative")
    return math.pi * radius ** 2
```
