#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
I/O utilities for magnetgeo package

This module provides file loading/saving utilities used throughout
the magnetgeo package for handling YAML, JSON, and other formats.
"""

import os
import yaml
import json
from typing import Any, Dict, Type, Union, Optional
from pathlib import Path


def load_file(filepath: str, expected_class: Optional[Type] = None, debug: bool = False) -> Any:
    """
    Load object from file (YAML or JSON)
    
    Args:
        filepath: Path to file to load
        expected_class: Expected class type (optional)
        debug: Whether to print debug information
        
    Returns:
        Loaded object
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file format not supported
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    filepath = Path(filepath)
    extension = filepath.suffix.lower()
    
    if debug:
        print(f"Loading file: {filepath} (expected: {expected_class})")
    
    try:
        with open(filepath, 'r') as f:
            if extension == '.yaml' or extension == '.yml':
                data = yaml.load(f, Loader=yaml.FullLoader)
            elif extension == '.json':
                data = json.load(f)
            else:
                # Try YAML first, then JSON
                content = f.read()
                f.seek(0)
                try:
                    data = yaml.load(f, Loader=yaml.FullLoader)
                except yaml.YAMLError:
                    try:
                        data = json.loads(content)
                    except json.JSONDecodeError:
                        raise ValueError(f"Unsupported file format: {extension}")
        
        if debug:
            print(f"Loaded data type: {type(data)}")
        
        # If expected_class is provided and data is dict, try to convert
        if expected_class and isinstance(data, dict) and hasattr(expected_class, 'from_dict'):
            if debug:
                print(f"Converting to {expected_class.__name__}")
            return expected_class.from_dict(data, debug=debug)
        
        return data
        
    except Exception as e:
        raise RuntimeError(f"Failed to load file {filepath}: {e}")


def write_file(obj: Any, format: str = 'yaml', filename: Optional[str] = None) -> None:
    """
    Write object to file
    
    Args:
        obj: Object to write
        format: Output format ('yaml' or 'json')
        filename: Optional filename override
        
    Raises:
        ValueError: If format not supported
    """
    if filename is None:
        if hasattr(obj, 'name') and obj.name:
            filename = f"{obj.name}.{format}"
        else:
            filename = f"output.{format}"
    
    if format.lower() == 'yaml':
        with open(filename, 'w') as f:
            yaml.dump(obj, f, default_flow_style=False)
    elif format.lower() == 'json':
        with open(filename, 'w') as f:
            if hasattr(obj, 'to_dict'):
                json.dump(obj.to_dict(), f, indent=4, sort_keys=True)
            else:
                # Try to serialize directly
                json.dump(obj, f, indent=4, sort_keys=True, default=str)
    else:
        raise ValueError(f"Unsupported format: {format}")


def load_objects(data: Union[str, list, dict], 
                expected_types: list, 
                type_map: Dict[str, Type],
                debug: bool = False) -> list:
    """
    Load multiple objects from various data sources
    
    Args:
        data: Data source (filepath, list of dicts, etc.)
        expected_types: List of expected object types
        type_map: Mapping from type names to classes
        debug: Whether to print debug information
        
    Returns:
        List of loaded objects
    """
    if not data:
        return []
    
    objects = []
    
    if isinstance(data, str):
        # Load from file
        loaded_data = load_file(data, debug=debug)
        if isinstance(loaded_data, list):
            objects.extend(loaded_data)
        else:
            objects.append(loaded_data)
    
    elif isinstance(data, list):
        # List of objects or dicts
        for item in data:
            if isinstance(item, dict):
                # Try to determine type and convert
                obj_type = item.get('__classname__') or item.get('type')
                if obj_type and obj_type in type_map:
                    cls = type_map[obj_type]
                    objects.append(cls.from_dict(item, debug=debug))
                else:
                    # Try each expected type
                    converted = False
                    for cls in expected_types:
                        try:
                            obj = cls.from_dict(item, debug=debug)
                            objects.append(obj)
                            converted = True
                            break
                        except Exception:
                            continue
                    
                    if not converted:
                        if debug:
                            print(f"Warning: Could not convert dict to expected types: {item}")
                        objects.append(item)  # Keep as dict
            else:
                objects.append(item)
    
    elif isinstance(data, dict):
        # Single object as dict
        obj_type = data.get('__classname__') or data.get('type')
        if obj_type and obj_type in type_map:
            cls = type_map[obj_type]
            objects.append(cls.from_dict(data, debug=debug))
        else:
            # Try each expected type
            converted = False
            for cls in expected_types:
                try:
                    obj = cls.from_dict(data, debug=debug)
                    objects.append(obj)
                    converted = True
                    break
                except Exception:
                    continue
            
            if not converted:
                objects.append(data)  # Keep as dict
    
    else:
        # Already an object
        objects.append(data)
    
    return objects


def ensure_directory(filepath: str) -> None:
    """
    Ensure directory exists for given filepath
    
    Args:
        filepath: Path to file (directory will be created if needed)
    """
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


def get_file_extension(filepath: str) -> str:
    """
    Get file extension in lowercase
    
    Args:
        filepath: Path to file
        
    Returns:
        File extension (without dot)
    """
    return Path(filepath).suffix.lower().lstrip('.')


def file_exists(filepath: str) -> bool:
    """
    Check if file exists
    
    Args:
        filepath: Path to check
        
    Returns:
        True if file exists
    """
    return os.path.exists(filepath) and os.path.isfile(filepath)


def backup_file(filepath: str, backup_suffix: str = '.bak') -> str:
    """
    Create backup of existing file
    
    Args:
        filepath: Path to file to backup
        backup_suffix: Suffix for backup file
        
    Returns:
        Path to backup file
        
    Raises:
        FileNotFoundError: If original file doesn't exist
    """
    if not file_exists(filepath):
        raise FileNotFoundError(f"Cannot backup non-existent file: {filepath}")
    
    backup_path = f"{filepath}{backup_suffix}"
    
    # If backup already exists, add number
    counter = 1
    while os.path.exists(backup_path):
        backup_path = f"{filepath}{backup_suffix}.{counter}"
        counter += 1
    
    import shutil
    shutil.copy2(filepath, backup_path)
    return backup_path


def safe_write_file(obj: Any, format: str = 'yaml', 
                   filename: Optional[str] = None,
                   backup: bool = True) -> None:
    """
    Safely write file with optional backup
    
    Args:
        obj: Object to write
        format: Output format
        filename: Optional filename
        backup: Whether to create backup of existing file
    """
    if filename is None:
        if hasattr(obj, 'name') and obj.name:
            filename = f"{obj.name}.{format}"
        else:
            filename = f"output.{format}"
    
    # Create backup if file exists
    if backup and file_exists(filename):
        backup_path = backup_file(filename)
        print(f"Created backup: {backup_path}")
    
    # Ensure directory exists
    ensure_directory(filename)
    
    # Write file
    write_file(obj, format, filename)


# Compatibility functions for existing code
def load_yaml_file(filepath: str, debug: bool = False) -> Any:
    """Load YAML file (compatibility function)"""
    return load_file(filepath, debug=debug)


def load_json_file(filepath: str, debug: bool = False) -> Any:
    """Load JSON file (compatibility function)"""
    return load_file(filepath, debug=debug)


def write_yaml_file(obj: Any, filename: str) -> None:
    """Write YAML file (compatibility function)"""
    write_file(obj, 'yaml', filename)


def write_json_file(obj: Any, filename: str) -> None:
    """Write JSON file (compatibility function)"""
    write_file(obj, 'json', filename)
