#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Probe class for measurement instrumentation in magnet systems
"""

from typing import Dict, Any, List, Tuple, Optional
from ...base.support_base import SupportComponentBase
from ...utils.validation import (
    validate_positive, validate_non_negative, 
    validate_enum_value, validate_string_not_empty
)
from ...utils.enums import ProbeType


class Probe(SupportComponentBase):
    """
    Probe definition for measurement instrumentation
    
    Probes are measurement devices positioned within magnet systems
    to monitor various parameters like voltage, temperature, or magnetic field.
    
    Attributes:
        name: Probe identifier
        probe_type: Type of probe ("voltage_taps", "temperature", "magnetic_field")
        position: [r, z, theta] coordinates
        parameters: Probe-specific parameters
        active: Whether probe is active/enabled
        measurement_range: Expected measurement range [min, max]
        accuracy: Measurement accuracy specification
    """
    
    yaml_tag = "!Probe"
    
    def __init__(
        self,
        name: str,
        probe_type: str,
        position: List[float],
        parameters: Dict[str, Any] = None,
        active: bool = True,
        measurement_range: List[float] = None,
        accuracy: float = None
    ):
        """
        Initialize probe
        
        Args:
            name: Probe identifier
            probe_type: Type of probe
            position: [r, z, theta] coordinates
            parameters: Probe-specific parameters
            active: Whether probe is active
            measurement_range: Expected range [min, max]
            accuracy: Measurement accuracy
        """
        super().__init__(name)
        self.probe_type = probe_type
        self.position = position or [0.0, 0.0, 0.0]
        self.parameters = parameters or {}
        self.active = active
        self.measurement_range = measurement_range or [0.0, 1.0]
        self.accuracy = accuracy
        
        # Call validation after setting all attributes
        self.validate()
    
    def validate(self) -> None:
        """Validate probe parameters"""
        super().validate()
        
        validate_string_not_empty(self.name, "name")
        validate_enum_value(self.probe_type, ProbeType, "probe_type")
        
        # Validate position
        if not isinstance(self.position, list) or len(self.position) != 3:
            raise ValueError("position must be [r, z, theta] coordinates")
        
        r, z, theta = self.position
        validate_non_negative(r, "position[0] (r)")
        # z can be negative, theta should be 0-360
        if not 0 <= theta <= 360:
            raise ValueError(f"position[2] (theta) must be 0-360°, got {theta}")
        
        # Validate measurement range
        if len(self.measurement_range) != 2:
            raise ValueError("measurement_range must be [min, max]")
        
        if self.measurement_range[0] >= self.measurement_range[1]:
            raise ValueError("measurement_range[0] must be < measurement_range[1]")
        
        # Validate accuracy if provided
        if self.accuracy is not None:
            validate_positive(self.accuracy, "accuracy")
        
        # Validate parameters based on probe type
        self._validate_type_specific_parameters()
    
    def _validate_type_specific_parameters(self) -> None:
        """Validate parameters specific to probe type"""
        if self.probe_type == "voltage_taps":
            self._validate_voltage_probe()
        elif self.probe_type == "temperature":
            self._validate_temperature_probe()
        elif self.probe_type == "magnetic_field":
            self._validate_magnetic_field_probe()
    
    def _validate_voltage_probe(self) -> None:
        """Validate voltage tap probe parameters"""
        # Voltage taps typically need connection points
        if "connections" in self.parameters:
            connections = self.parameters["connections"]
            if not isinstance(connections, list) or len(connections) < 2:
                raise ValueError("Voltage probe needs at least 2 connections")
    
    def _validate_temperature_probe(self) -> None:
        """Validate temperature probe parameters"""
        # Temperature probes might have sensor type, calibration, etc.
        if "sensor_type" in self.parameters:
            valid_sensors = ["thermocouple", "rtd", "thermistor"]
            if self.parameters["sensor_type"] not in valid_sensors:
                raise ValueError(f"sensor_type must be one of {valid_sensors}")
    
    def _validate_magnetic_field_probe(self) -> None:
        """Validate magnetic field probe parameters"""
        # B-field probes might have orientation, calibration constants
        if "orientation" in self.parameters:
            orientation = self.parameters["orientation"]
            if not isinstance(orientation, list) or len(orientation) != 3:
                raise ValueError("orientation must be [x, y, z] unit vector")
    
    def get_cylindrical_position(self) -> Tuple[float, float, float]:
        """
        Get position in cylindrical coordinates
        
        Returns:
            Tuple of (r, z, theta) in consistent units
        """
        return tuple(self.position)
    
    def get_cartesian_position(self) -> Tuple[float, float, float]:
        """
        Convert position to Cartesian coordinates
        
        Returns:
            Tuple of (x, y, z) coordinates
        """
        import math
        r, z, theta_deg = self.position
        theta_rad = math.radians(theta_deg)
        
        x = r * math.cos(theta_rad)
        y = r * math.sin(theta_rad)
        
        return (x, y, z)
    
    def is_in_range(self, value: float) -> bool:
        """
        Check if measured value is within expected range
        
        Args:
            value: Measured value
            
        Returns:
            True if value is within measurement_range
        """
        return self.measurement_range[0] <= value <= self.measurement_range[1]
    
    def get_expected_units(self) -> str:
        """
        Get expected measurement units based on probe type
        
        Returns:
            Unit string
        """
        unit_map = {
            "voltage_taps": "V",
            "temperature": "K",
            "magnetic_field": "T"
        }
        return unit_map.get(self.probe_type, "unknown")
    
    def get_probe_info(self) -> Dict[str, Any]:
        """
        Get comprehensive probe information
        
        Returns:
            Dictionary with probe properties
        """
        r, z, theta = self.position
        x, y, z_cart = self.get_cartesian_position()
        
        return {
            "name": self.name,
            "type": self.probe_type,
            "active": self.active,
            "position_cylindrical": {"r": r, "z": z, "theta": theta},
            "position_cartesian": {"x": x, "y": y, "z": z_cart},
            "measurement_range": self.measurement_range,
            "expected_units": self.get_expected_units(),
            "accuracy": self.accuracy,
            "parameters": self.parameters
        }
    
    def set_position(self, r: float, z: float, theta: float) -> None:
        """
        Update probe position
        
        Args:
            r: Radial coordinate
            z: Axial coordinate  
            theta: Angular coordinate (degrees)
        """
        self.position = [r, z, theta]
        # Re-validate position
        self.validate()
    
    def activate(self) -> None:
        """Activate the probe"""
        self.active = True
    
    def deactivate(self) -> None:
        """Deactivate the probe"""
        self.active = False
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], debug: bool = False) -> 'Probe':
        """
        Create Probe from dictionary
        
        Args:
            data: Dictionary with probe parameters
            debug: Whether to print debug info
            
        Returns:
            Probe instance
        """
        if debug:
            print(f"Creating Probe from: {data}")
        
        name = data["name"]
        probe_type = data["probe_type"]
        position = data.get("position", [0.0, 0.0, 0.0])
        parameters = data.get("parameters", {})
        active = data.get("active", True)
        measurement_range = data.get("measurement_range", [0.0, 1.0])
        accuracy = data.get("accuracy")
        
        return cls(
            name=name,
            probe_type=probe_type,
            position=position,
            parameters=parameters,
            active=active,
            measurement_range=measurement_range,
            accuracy=accuracy
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        result = {
            "name": self.name,
            "probe_type": self.probe_type,
            "position": self.position,
            "parameters": self.parameters,
            "active": self.active,
            "measurement_range": self.measurement_range
        }
        
        if self.accuracy is not None:
            result["accuracy"] = self.accuracy
        
        return result
    
    def __repr__(self) -> str:
        """String representation"""
        return (f"{self.__class__.__name__}(name={self.name}, "
                f"type={self.probe_type}, position={self.position}, "
                f"active={self.active})")


# Factory functions for common probe types

def create_voltage_tap(name: str, r: float, z: float, theta: float = 0.0,
                      voltage_range: List[float] = None) -> Probe:
    """
    Create voltage tap probe
    
    Args:
        name: Probe name
        r: Radial position
        z: Axial position
        theta: Angular position (degrees)
        voltage_range: Expected voltage range [min, max]
        
    Returns:
        Voltage tap probe
    """
    if voltage_range is None:
        voltage_range = [-10.0, 10.0]  # Default ±10V range
    
    return Probe(
        name=name,
        probe_type="voltage_taps",
        position=[r, z, theta],
        measurement_range=voltage_range,
        parameters={"connections": ["positive", "negative"]}
    )


def create_temperature_probe(name: str, r: float, z: float, theta: float = 0.0,
                           temp_range: List[float] = None, 
                           sensor_type: str = "thermocouple") -> Probe:
    """
    Create temperature probe
    
    Args:
        name: Probe name
        r: Radial position
        z: Axial position
        theta: Angular position (degrees)
        temp_range: Expected temperature range [min, max] in Kelvin
        sensor_type: Type of temperature sensor
        
    Returns:
        Temperature probe
    """
    if temp_range is None:
        temp_range = [4.0, 300.0]  # Default 4K to 300K range
    
    return Probe(
        name=name,
        probe_type="temperature",
        position=[r, z, theta],
        measurement_range=temp_range,
        parameters={"sensor_type": sensor_type}
    )


def create_magnetic_field_probe(name: str, r: float, z: float, theta: float = 0.0,
                               field_range: List[float] = None,
                               orientation: List[float] = None) -> Probe:
    """
    Create magnetic field probe
    
    Args:
        name: Probe name
        r: Radial position
        z: Axial position
        theta: Angular position (degrees)
        field_range: Expected field range [min, max] in Tesla
        orientation: Field measurement direction [x, y, z]
        
    Returns:
        Magnetic field probe
    """
    if field_range is None:
        field_range = [0.0, 45.0]  # Default 0-45T range
    
    if orientation is None:
        orientation = [0.0, 0.0, 1.0]  # Default z-direction
    
    return Probe(
        name=name,
        probe_type="magnetic_field",
        position=[r, z, theta],
        measurement_range=field_range,
        parameters={"orientation": orientation}
    )


def Probe_constructor(loader, node):
    """YAML constructor for backward compatibility"""
    values = loader.construct_mapping(node)
    return Probe.from_dict(values)


# Register YAML constructor
import yaml
yaml.add_constructor("!Probe", Probe_constructor)
