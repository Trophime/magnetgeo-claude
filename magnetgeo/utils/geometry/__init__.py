#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Geometry utilities for magnetgeo package

This module provides geometric classes and utilities for 2D and 3D operations.
"""

from .shape2d import Shape2D, create_circle, create_rectangle

__all__ = [
    'Shape2D',
    'create_circle', 
    'create_rectangle'
]