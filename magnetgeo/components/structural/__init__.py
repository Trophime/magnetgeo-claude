#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Structural components for magnetgeo

This module contains structural components that provide physical support
and electrical connections in magnet assemblies.
"""

from .ring import Ring
from .screen import Screen
from .innercurrentlead import InnerCurrentLead
from .outercurrentlead import OuterCurrentLead

__all__ = ["Ring", "Screen", "InnerCurrentLead", "OuterCurrentLead"]
