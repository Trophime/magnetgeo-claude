#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
HTS component factory functions

Provides convenience functions for creating common HTS geometric configurations
without requiring detailed knowledge of individual component parameters.
"""

from typing import Dict, Any, List
from .tape import Tape, create_rebco_tape, create_bismuth_tape
from .pancake import Pancake, create_uniform_pancake
from .isolation import Isolation, create_uniform_isolation, create_kapton_isolation
from .dblpancake import DblPancake, create_symmetric_dblpancake
from .structure import HTSinsert

try:
    from ...utils.validation import validate_positive, validate_non_negative, validate_string_not_empty
    VALIDATION_AVAILABLE = True
except ImportError:
    VALIDATION_AVAILABLE = False
    def validate_positive(val, name): pass
    def validate_non_negative(val, name): pass
    def validate_string_not_empty(val, name): pass


def create_uniform_structure(
    name: str,
    r0: float,
    r1: float,
    height: float,
    n_dblpancakes: int,
    tape_type: str = "rebco",
    isolation_height: float = 0.2
) -> HTSinsert:
    """
    Create uniform HTS structure with identical double pancakes
    
    Args:
        name: Insert name
        r0: Inner radius (mm)
        r1: Outer radius (mm)
        height: Total height (mm)
        n_dblpancakes: Number of double pancakes
        tape_type: Type of tape ("rebco" or "bismuth")
        isolation_height: Height of isolation between double pancakes (mm)
        
    Returns:
        HTSinsert instance with uniform structure
    """
    if VALIDATION_AVAILABLE:
        validate_string_not_empty(name, "name")
        validate_positive(r1 - r0, "radial width")
        validate_positive(height, "height")
        validate_positive(n_dblpancakes, "n_dblpancakes")
        validate_non_negative(isolation_height, "isolation_height")
    
    # Create tape based on type
    if tape_type == "rebco":
        tape = create_rebco_tape()
    elif tape_type == "bismuth":
        tape = create_bismuth_tape()
    else:
        # Default REBCO with custom width
        radial_width = r1 - r0
        tape_width = radial_width / 20  # Assume 20 turns per pancake
        tape = Tape(w=tape_width * 0.9, h=0.1, e=tape_width * 0.1)
    
    # Create pancake that fills the radial space
    pancake = create_uniform_pancake(
        r0=r0,
        r1=r1,
        height=height / (n_dblpancakes * 2),  # Each DP has 2 pancakes
        tape_width=tape.getW()
    )
    pancake.tape = tape  # Use specified tape
    
    # Create double pancakes
    dblpancakes = []
    isolations = []
    
    # Calculate spacing
    dp_height = height / n_dblpancakes
    z_start = -height / 2
    
    for i in range(n_dblpancakes):
        z_center = z_start + (i + 0.5) * dp_height
        
        # Create isolation for pancakes within double pancake
        dp_isolation = create_kapton_isolation(
            r0=r0,
            thickness=r1 - r0,
            height=0.1  # Thin Kapton between pancakes
        )
        
        dp = DblPancake(z_center, pancake, dp_isolation)
        dblpancakes.append(dp)
        
        # Create isolation between double pancakes (except after last)
        if i < n_dblpancakes - 1:
            isolation = create_uniform_isolation(r0, r1 - r0, isolation_height)
            isolations.append(isolation)
    
    return HTSinsert(
        name=name,
        z0=0.0,
        h=height,
        r0=r0,
        r1=r1,
        z1=-height/2,
        n=n_dblpancakes,
        dblpancakes=dblpancakes,
        isolations=isolations
    )


def create_from_config(config_path: str, debug: bool = False) -> HTSinsert:
    """
    Create HTS structure from configuration file
    
    Args:
        config_path: Path to JSON configuration file
        debug: Whether to print debug information
        
    Returns:
        HTSinsert instance loaded from configuration
    """
    return HTSinsert.fromcfg(config_path, debug=debug)


def create_solenoid_structure(
    name: str,
    r0: float,
    n_turns_per_pancake: int,
    n_dblpancakes: int,
    tape_width: float = 4.0,
    tape_height: float = 0.1,
    spacing_factor: float = 1.1
) -> HTSinsert:
    """
    Create solenoid-style HTS structure
    
    Args:
        name: Insert name
        r0: Inner radius (mm)
        n_turns_per_pancake: Number of turns per pancake
        n_dblpancakes: Number of double pancakes
        tape_width: Tape width (mm)
        tape_height: Tape height (mm)
        spacing_factor: Spacing factor between components
        
    Returns:
        HTSinsert instance with solenoid geometry
    """
    if VALIDATION_AVAILABLE:
        validate_string_not_empty(name, "name")
        validate_positive(r0, "r0")
        validate_positive(n_turns_per_pancake, "n_turns_per_pancake")
        validate_positive(n_dblpancakes, "n_dblpancakes")
        validate_positive(tape_width, "tape_width")
        validate_positive(tape_height, "tape_height")
    
    # Create tape
    tape = Tape(w=tape_width * 0.9, h=tape_height, e=tape_width * 0.1)
    
    # Create pancake
    pancake = Pancake(
        r0=r0,
        tape=tape,
        n=n_turns_per_pancake,
        mandrin=r0 * 0.95  # Mandrel slightly smaller
    )
    
    # Calculate dimensions
    r1 = pancake.getR1()
    radial_width = r1 - r0
    
    # Create double pancakes with spacing
    dblpancakes = []
    isolations = []
    
    dp_height = tape_height * 2 + 0.2  # Two pancakes + thin isolation
    total_height = n_dblpancakes * dp_height * spacing_factor
    
    z_start = -total_height / 2
    z_step = total_height / n_dblpancakes
    
    for i in range(n_dblpancakes):
        z_center = z_start + (i + 0.5) * z_step
        
        # Isolation within double pancake
        dp_isolation = create_kapton_isolation(r0, radial_width, 0.1, 1)
        
        dp = DblPancake(z_center, pancake, dp_isolation)
        dblpancakes.append(dp)
        
        # Isolation between double pancakes
        if i < n_dblpancakes - 1:
            iso_height = z_step - dp_height
            if iso_height > 0:
                isolation = create_uniform_isolation(r0, radial_width, iso_height)
                isolations.append(isolation)
    
    return HTSinsert(
        name=name,
        z0=0.0,
        h=total_height,
        r0=r0,
        r1=r1,
        z1=-total_height/2,
        n=n_dblpancakes,
        dblpancakes=dblpancakes,
        isolations=isolations
    )


def create_graded_structure(
    name: str,
    r0: float,
    r1: float,
    height: float,
    n_dblpancakes: int,
    turn_distribution: str = "linear"
) -> HTSinsert:
    """
    Create HTS structure with graded turn distribution
    
    Args:
        name: Insert name
        r0: Inner radius (mm)
        r1: Outer radius (mm)
        height: Total height (mm)
        n_dblpancakes: Number of double pancakes
        turn_distribution: Distribution type ("linear", "quadratic", "uniform")
        
    Returns:
        HTSinsert instance with graded structure
    """
    if VALIDATION_AVAILABLE:
        validate_string_not_empty(name, "name")
        validate_positive(r1 - r0, "radial width")
        validate_positive(height, "height")
        validate_positive(n_dblpancakes, "n_dblpancakes")
    
    # Base tape
    tape = create_rebco_tape(width=3.0, height=0.1)
    radial_width = r1 - r0
    max_turns = int(radial_width / tape.getW())
    
    # Calculate turn distribution
    turn_counts = []
    if turn_distribution == "linear":
        for i in range(n_dblpancakes):
            factor = (i + 1) / n_dblpancakes
            turns = int(max_turns * factor)
            turn_counts.append(max(1, turns))
    elif turn_distribution == "quadratic":
        for i in range(n_dblpancakes):
            factor = ((i + 1) / n_dblpancakes) ** 2
            turns = int(max_turns * factor)
            turn_counts.append(max(1, turns))
    else:  # uniform
        uniform_turns = max(1, max_turns // 2)
        turn_counts = [uniform_turns] * n_dblpancakes
    
    # Create double pancakes with varying turn counts
    dblpancakes = []
    isolations = []
    
    dp_height = height / n_dblpancakes
    z_start = -height / 2
    
    for i in range(n_dblpancakes):
        z_center = z_start + (i + 0.5) * dp_height
        
        # Create pancake with specific turn count
        pancake = Pancake(
            r0=r0,
            tape=tape,
            n=turn_counts[i],
            mandrin=r0 * 0.95
        )
        
        # Isolation within double pancake
        dp_isolation = create_kapton_isolation(r0, radial_width, 0.15)
        
        dp = DblPancake(z_center, pancake, dp_isolation)
        dblpancakes.append(dp)
        
        # Isolation between double pancakes
        if i < n_dblpancakes - 1:
            isolation = create_uniform_isolation(r0, radial_width, 0.5)
            isolations.append(isolation)
    
    # Calculate actual r1 from maximum pancake extent
    actual_r1 = max(dp.getR1() for dp in dblpancakes)
    
    return HTSinsert(
        name=name,
        z0=0.0,
        h=height,
        r0=r0,
        r1=actual_r1,
        z1=-height/2,