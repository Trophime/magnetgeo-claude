from abc import ABC, abstractmethod
from typing import Tuple, List

class GeometryMixin(ABC):
    """
    Mixin providing common geometry operations
    
    This mixin defines the interface for all geometric objects
    in the magnetgeo package.
    """
    
    @abstractmethod
    def get_bounds(self) -> Tuple[List[float], List[float]]:
        """
        Return geometric bounds for this object
        
        Returns:
            Tuple of (r_bounds, z_bounds) where each is [min, max]
        """
        pass
    
    def boundingBox(self) -> Tuple[List[float], List[float]]:
        """
        Return bounding box as (r, z) tuple
        
        Alias for get_bounds() for backward compatibility.
        
        Returns:
            Tuple of (r_bounds, z_bounds)
        """
        return self.get_bounds()
    
    def intersect(self, r: List[float], z: List[float]) -> bool:
        """
        Check if intersection with rectangle defined by r,z is non-empty
        
        Args:
            r: Radial bounds [r_min, r_max] of test rectangle
            z: Axial bounds [z_min, z_max] of test rectangle
            
        Returns:
            True if objects intersect, False if no intersection
        """
        r_bounds, z_bounds = self.get_bounds()
        
        # Check if rectangles overlap in both dimensions
        r_overlap = r_bounds[0] < r[1] and r[0] < r_bounds[1]
        z_overlap = z_bounds[0] < z[1] and z[0] < z_bounds[1]
        
        return r_overlap and z_overlap
    
    def get_lc(self) -> float:
        """
        Get characteristic length for meshing
        
        Default implementation uses 1/10 of smallest dimension.
        Override in subclasses for custom meshing requirements.
        
        Returns:
            Characteristic length for mesh generation
        """
        r_bounds, z_bounds = self.get_bounds()
        dr = r_bounds[1] - r_bounds[0]
        dz = z_bounds[1] - z_bounds[0]
        return min(dr, dz) / 10.0
    
    def get_center(self) -> Tuple[float, float]:
        """
        Get geometric center of object
        
        Returns:
            Tuple of (r_center, z_center)
        """
        r_bounds, z_bounds = self.get_bounds()
        r_center = (r_bounds[0] + r_bounds[1]) / 2
        z_center = (z_bounds[0] + z_bounds[1]) / 2
        return (r_center, z_center)
    
    def get_volume_2d(self) -> float:
        """
        Get 2D volume (area in r-z plane) of object
        
        Assumes axisymmetric geometry and calculates cylindrical volume.
        
        Returns:
            Volume in cylindrical coordinates
        """
        r_bounds, z_bounds = self.get_bounds()
        r_outer = r_bounds[1]
        r_inner = r_bounds[0]
        height = z_bounds[1] - z_bounds[0]
        
        import math
        return math.pi * (r_outer**2 - r_inner**2) * height

class CollectionGeometryMixin(GeometryMixin):
    """
    Mixin for collections of geometric objects
    
    This mixin provides geometry operations for containers that
    hold multiple geometric objects.
    """
    
    @abstractmethod
    def get_objects(self) -> List[GeometryMixin]:
        """
        Return list of geometric objects in this collection
        
        Returns:
            List of objects that implement GeometryMixin
        """
        pass
    
    def get_bounds(self) -> Tuple[List[float], List[float]]:
        """
        Calculate bounding box from all contained objects
        
        Returns:
            Combined bounding box of all objects
        """
        objects = self.get_objects()
        if not objects:
            return ([0, 0], [0, 0])
        
        # Get bounds from first object
        r_bounds, z_bounds = objects[0].get_bounds()
        r_min, r_max = r_bounds[0], r_bounds[1]
        z_min, z_max = z_bounds[0], z_bounds[1]
        
        # Expand bounds to include all objects
        for obj in objects[1:]:
            obj_r, obj_z = obj.get_bounds()
            r_min = min(r_min, obj_r[0])
            r_max = max(r_max, obj_r[1])
            z_min = min(z_min, obj_z[0])
            z_max = max(z_max, obj_z[1])
        
        return ([r_min, r_max], [z_min, z_max])
    
    def get_total_volume(self) -> float:
        """
        Get total volume of all contained objects
        
        Returns:
            Sum of volumes of all objects
        """
        return sum(obj.get_volume_2d() for obj in self.get_objects())
    
    def find_overlapping_objects(self, tolerance: float = 1e-6) -> List[Tuple[GeometryMixin, GeometryMixin]]:
        """
        Find pairs of overlapping objects
        
        Args:
            tolerance: Minimum overlap to consider significant
            
        Returns:
            List of tuples containing overlapping object pairs
        """
        objects = self.get_objects()
        overlapping_pairs = []
        
        for i, obj1 in enumerate(objects):
            for obj2 in objects[i+1:]:
                r1, z1 = obj1.get_bounds()
                r2, z2 = obj2.get_bounds()
                
                # Check for meaningful overlap (not just touching)
                r_overlap = max(0, min(r1[1], r2[1]) - max(r1[0], r2[0]))
                z_overlap = max(0, min(z1[1], z2[1]) - max(z1[0], z2[0]))
                
                if r_overlap > tolerance and z_overlap > tolerance:
                    overlapping_pairs.append((obj1, obj2))
        
        return overlapping_pairs
