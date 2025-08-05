#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Refactored ModelAxi class with validation and enhanced functionality
"""

from typing import Dict, Any, List, Tuple
from ...base.support_base import SupportComponentBase
from ...utils.validation import validate_non_negative, validate_list_length


class ModelAxi(SupportComponentBase):
    """
    Axisymmetric model definition with improved validation
    
    Defines the helical cutting pattern for generating magnet windings.
    The model specifies the number of turns and pitch for each section.
    
    Attributes:
        name: Model identifier
        h: Total height of the helical pattern
        turns: List of turn counts for each section
        pitch: List of pitch values for each section
    """
    
    yaml_tag = "!ModelAxi"
    
    def __init__(
        self,
        name: str = "",
        h: float = 0.0,
        turns: List[float] = None,
        pitch: List[float] = None
    ):
        """
        Initialize axisymmetric model
        
        Args:
            name: Model identifier
            h: Total height of helical pattern
            turns: List of turn counts for each section
            pitch: List of pitch values for each section
        """
        super().__init__(name)
        self.h = h
        self.turns = turns or []
        self.pitch = pitch or []
        
        # Call validation after setting all attributes
        self.validate()
    
    def validate(self) -> None:
        """Validate model parameters"""
        super().validate()
        
        validate_non_negative(self.h, "h")
        
        # Validate that turns and pitch have same length
        if len(self.turns) != len(self.pitch):
            raise ValueError(
                f"turns and pitch must have same length: "
                f"got {len(self.turns)} turns and {len(self.pitch)} pitch values"
            )
        
        # Validate individual values
        for i, turn_count in enumerate(self.turns):
            if turn_count < 0:
                raise ValueError(f"turns[{i}] must be non-negative, got {turn_count}")
        
        for i, pitch_value in enumerate(self.pitch):
            if pitch_value < 0:
                raise ValueError(f"pitch[{i}] must be non-negative, got {pitch_value}")
    
    def get_total_turns(self) -> float:
        """
        Calculate total number of turns
        
        Returns:
            Sum of all turn values
        """
        return sum(self.turns)
    
    def get_Nturns(self) -> float:
        """Alias for get_total_turns() for backward compatibility"""
        return self.get_total_turns()
    
    def get_section_count(self) -> int:
        """Get number of sections in the model"""
        return len(self.turns)
    
    def get_total_length(self) -> float:
        """
        Calculate total helical length based on turns and pitch
        
        Returns:
            Total length of helical path
        """
        total_length = 0.0
        for turns, pitch in zip(self.turns, self.pitch):
            # Length = turns * pitch for each section
            total_length += turns * pitch
        return total_length
    
    def compact(self, tol: float = 1.0e-6) -> Tuple[List[float], List[float]]:
        """
        Compact consecutive sections with same pitch
        
        Combines adjacent sections that have the same pitch value
        (within tolerance) to reduce the number of sections.
        
        Args:
            tol: Tolerance for pitch comparison
            
        Returns:
            Tuple of (compacted_turns, compacted_pitch)
        """
        if not self.turns or not self.pitch:
            return ([], [])
        
        def indices(lst: List[float], item: float) -> List[int]:
            """Find indices where list values match item within tolerance"""
            return [i for i, x in enumerate(lst) if abs(1 - item / x) <= tol if x != 0]
        
        # Find duplicate pitch values
        pitch_list = self.pitch
        duplicates = {}
        for pitch_val in set(pitch_list):
            if pitch_val != 0:  # Avoid division by zero
                duplicate_indices = indices(pitch_list, pitch_val)
                if len(duplicate_indices) > 1:
                    duplicates[pitch_val] = duplicate_indices
        
        # Group consecutive duplicates
        sum_index = {}
        for pitch_val in duplicates:
            duplicate_indices = duplicates[pitch_val]
            index_fst = duplicate_indices[0]
            sum_index[index_fst] = [index_fst]
            current_group = sum_index[index_fst]
            
            for idx in duplicate_indices[1:]:
                if idx - current_group[-1] == 1:
                    # Consecutive index
                    current_group.append(idx)
                else:
                    # Start new group
                    sum_index[idx] = [idx]
                    current_group = sum_index[idx]
        
        # Identify indices to remove (all except first in each group)
        remove_ids = []
        for group_start in sum_index:
            for idx in sum_index[group_start][1:]:  # Skip first in group
                remove_ids.append(idx)
        
        # Create compacted lists
        new_pitch = [p for i, p in enumerate(self.pitch) if i not in remove_ids]
        
        # Sum turns for combined sections
        new_turns = self.turns.copy()
        for group_start in sum_index:
            for idx in sum_index[group_start][1:]:  # Skip first in group
                new_turns[group_start] += self.turns[idx]
        
        new_turns = [t for i, t in enumerate(new_turns) if i not in remove_ids]
        
        return (new_turns, new_pitch)
    
    def apply_compaction(self, tol: float = 1.0e-6) -> None:
        """
        Apply compaction to this model in-place
        
        Args:
            tol: Tolerance for pitch comparison
        """
        new_turns, new_pitch = self.compact(tol)
        self.turns = new_turns
        self.pitch = new_pitch
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], debug: bool = False) -> 'ModelAxi':
        """
        Create ModelAxi from dictionary
        
        Args:
            data: Dictionary with model parameters
            debug: Whether to print debug info
            
        Returns:
            ModelAxi instance
        """
        if debug:
            print(f"Creating ModelAxi from: {data}")
        
        name = data.get("name", "")
        h = data.get("h", 0.0)
        turns = data.get("turns", [])
        pitch = data.get("pitch", [])
        
        return cls(name=name, h=h, turns=turns, pitch=pitch)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "name": self.name,
            "h": self.h,
            "turns": self.turns,
            "pitch": self.pitch
        }
    
    def __repr__(self) -> str:
        """String representation"""
        return (f"{self.__class__.__name__}(name={self.name}, h={self.h}, "
                f"turns={self.turns}, pitch={self.pitch})")


def ModelAxi_constructor(loader, node):
    """YAML constructor for backward compatibility"""
    values = loader.construct_mapping(node)
    return ModelAxi.from_dict(values)


# Register YAML constructor
import yaml
yaml.add_constructor("!ModelAxi", ModelAxi_constructor)
