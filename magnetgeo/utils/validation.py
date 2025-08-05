from typing import List, Any

def validate_positive(value: float, name: str) -> None:
    """
    Validate that a value is positive
    
    Args:
        value: Value to validate
        name: Parameter name for error messages
        
    Raises:
        ValueError: If value is not positive
    """
    if not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be numeric, got {type(value).__name__}")
    
    if value <= 0:
        raise ValueError(f"{name} must be positive, got {value}")

def validate_non_negative(value: float, name: str) -> None:
    """
    Validate that a value is non-negative
    
    Args:
        value: Value to validate
        name: Parameter name for error messages
        
    Raises:
        ValueError: If value is negative
    """
    if not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be numeric, got {type(value).__name__}")
    
    if value < 0:
        raise ValueError(f"{name} must be non-negative, got {value}")

def validate_angle(value: float, min_deg: float, max_deg: float, name: str) -> None:
    """
    Validate angle is within specified range
    
    Args:
        value: Angle value in degrees
        min_deg: Minimum allowed angle
        max_deg: Maximum allowed angle
        name: Parameter name for error messages
        
    Raises:
        ValueError: If angle is outside valid range
    """
    if not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be numeric, got {type(value).__name__}")
    
    if not min_deg <= value <= max_deg:
        raise ValueError(f"{name} must be between {min_deg}° and {max_deg}°, got {value}°")

def validate_bounds(r: List[float], z: List[float]) -> None:
    """
    Validate geometric bounds for components
    
    Args:
        r: Radial bounds [r_min, r_max]
        z: Axial bounds [z_min, z_max]
        
    Raises:
        ValueError: If bounds are invalid
        TypeError: If bounds are not proper lists
    """
    # Type validation
    if not isinstance(r, list) or not isinstance(z, list):
        raise TypeError("Bounds must be lists")
    
    if len(r) != 2 or len(z) != 2:
        raise ValueError("Bounds must be [min, max] pairs")
    
    # Validate numeric values
    for i, val in enumerate(r):
        if not isinstance(val, (int, float)):
            raise TypeError(f"r[{i}] must be numeric, got {type(val).__name__}")
    
    for i, val in enumerate(z):
        if not isinstance(val, (int, float)):
            raise TypeError(f"z[{i}] must be numeric, got {type(val).__name__}")
    
    # Range validation
    if r[0] >= r[1]:
        raise ValueError(f"r_min ({r[0]}) must be less than r_max ({r[1]})")
    
    if r[0] < 0:
        raise ValueError("Radial coordinates must be non-negative")
    
    if z[0] >= z[1]:
        raise ValueError(f"z_min ({z[0]}) must be less than z_max ({z[1]})")

def validate_enum_value(value: str, enum_class: type, name: str) -> None:
    """
    Validate that string value is valid for enum
    
    Args:
        value: String value to validate
        enum_class: Enum class to validate against
        name: Parameter name for error messages
        
    Raises:
        ValueError: If value is not valid for enum
        TypeError: If value is not a string
    """
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string, got {type(value).__name__}")
    
    valid_values = [e.value for e in enum_class]
    if value not in valid_values:
        raise ValueError(f"{name} must be one of {valid_values}, got '{value}'")

def validate_list_length(lst: List[Any], expected_length: int, name: str) -> None:
    """
    Validate list has expected length
    
    Args:
        lst: List to validate
        expected_length: Expected length
        name: Parameter name for error messages
        
    Raises:
        ValueError: If list length doesn't match expected
        TypeError: If input is not a list
    """
    if not isinstance(lst, list):
        raise TypeError(f"{name} must be a list, got {type(lst).__name__}")
    
    if len(lst) != expected_length:
        raise ValueError(f"{name} must have length {expected_length}, got {len(lst)}")

def validate_string_not_empty(value: str, name: str) -> None:
    """
    Validate that string is not empty
    
    Args:
        value: String to validate
        name: Parameter name for error messages
        
    Raises:
        ValueError: If string is empty
        TypeError: If value is not a string
    """
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string, got {type(value).__name__}")
    
    if not value.strip():
        raise ValueError(f"{name} cannot be empty")
