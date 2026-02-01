#!/usr/bin/env python3
"""
Layout Scaling Engine - Calculates character positions based on measurements
Supports scaling and zoom functionality for accurate ASCII layouts
"""

import json
import math
from typing import Dict, Tuple, List, Optional

class LayoutEngine:
    def __init__(self, config_path: str = "scripts/config/kitchen_measurements.json"):
        """
        Initialize the layout engine with measurements
        """
        self.config_path = config_path
        self.measurements = self.load_measurements()
        
        # Default scaling: 1 character = 1 inch
        self.base_scale = 1.0  # characters per inch
        self.current_scale = 1.0
        self.zoom_level = 1.0
        
        # Layout boundaries
        self.max_width = 120  # max characters horizontally
        self.max_height = 40  # max characters vertically
        
    def load_measurements(self) -> Dict:
        """Load measurements from config file"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Config file {self.config_path} not found")
            return {"wall_measurements": {}}
    
    def calculate_chars_from_inches(self, inches: float, scale: Optional[float] = None) -> int:
        """
        Calculate number of characters needed for given inches
        """
        if scale is None:
            scale = self.current_scale * self.zoom_level
            
        chars = inches * self.base_scale * scale
        
        # Round to nearest integer, minimum 1 character
        return max(1, round(chars))
    
    def calculate_inches_from_chars(self, chars: int, scale: Optional[float] = None) -> float:
        """
        Calculate inches represented by number of characters
        """
        if scale is None:
            scale = self.current_scale * self.zoom_level
            
        return chars / (self.base_scale * scale)
    
    def calculate_wall_segments(self) -> Dict[str, Dict]:
        """
        Calculate character counts for each wall segment
        """
        segments = {}
        
        for segment_id, segment_data in self.measurements.get("wall_measurements", {}).items():
            inches = segment_data["measurement_inches"]
            chars = self.calculate_chars_from_inches(inches)
            
            segments[segment_id] = {
                "inches": inches,
                "chars": chars,
                "type": segment_data["type"],
                "symbol": segment_data["symbol"]
            }
            
        return segments
    
    def calculate_total_room_dimensions(self) -> Tuple[int, int]:
        """
        Calculate total room dimensions in characters
        Returns (width_chars, height_chars)
        """
        segments = self.calculate_wall_segments()
        
        # Calculate width from North wall segments (N1 + N2)
        width_chars = 0
        for segment_id in ["N1", "N2"]:
            if segment_id in segments:
                width_chars += segments[segment_id]["chars"]
        
        # Calculate height from West wall segments (W1 + W2 + W3)
        height_chars = 0
        for segment_id in ["W1", "W2", "W3"]:
            if segment_id in segments:
                height_chars += segments[segment_id]["chars"]
        
        return width_chars, height_chars
    
    def auto_scale_to_fit(self, max_width: Optional[int] = None, max_height: Optional[int] = None) -> float:
        """
        Automatically calculate scale to fit within boundaries
        """
        if max_width is None:
            max_width = self.max_width
        if max_height is None:
            max_height = self.max_height
            
        current_width, current_height = self.calculate_total_room_dimensions()
        
        if current_width == 0 or current_height == 0:
            return self.current_scale
        
        # Calculate scale factors for width and height
        width_scale = max_width / current_width
        height_scale = max_height / current_height
        
        # Use the smaller scale factor to fit both dimensions
        new_scale = min(width_scale, height_scale)
        
        # Don't scale up beyond 1.0 by default
        new_scale = min(new_scale, 1.0)
        
        self.current_scale = new_scale
        return new_scale
    
    def set_zoom(self, zoom_level: float) -> None:
        """
        Set zoom level (1.0 = normal, < 1.0 = zoom out, > 1.0 = zoom in)
        """
        self.zoom_level = max(0.1, min(5.0, zoom_level))  # Limit zoom range
    
    def get_effective_scale(self) -> float:
        """Get the current effective scale (base scale * current scale * zoom)"""
        return self.base_scale * self.current_scale * self.zoom_level
    
    def generate_scaled_layout_data(self) -> Dict:
        """
        Generate complete layout data with current scaling
        """
        segments = self.calculate_wall_segments()
        width_chars, height_chars = self.calculate_total_room_dimensions()
        
        return {
            "segments": segments,
            "total_dimensions": {
                "width_chars": width_chars,
                "height_chars": height_chars,
                "effective_scale": self.get_effective_scale(),
                "base_scale": self.base_scale,
                "current_scale": self.current_scale,
                "zoom_level": self.zoom_level
            },
            "boundaries": {
                "max_width": self.max_width,
                "max_height": self.max_height
            }
        }
    
    def print_scale_info(self) -> None:
        """Print current scaling information"""
        data = self.generate_scaled_layout_data()
        dims = data["total_dimensions"]
        
        print(f"\nLayout Engine Scaling Information:")
        print(f"  Base Scale: {self.base_scale:.2f} chars/inch")
        print(f"  Current Scale: {self.current_scale:.2f}")
        print(f"  Zoom Level: {self.zoom_level:.2f}x")
        print(f"  Effective Scale: {dims['effective_scale']:.2f} chars/inch")
        print(f"  Layout Dimensions: {dims['width_chars']} x {dims['height_chars']} chars")
        print(f"  Max Boundaries: {self.max_width} x {self.max_height} chars")
    
    def print_wall_segments_info(self) -> None:
        """Print detailed information about wall segments"""
        segments = self.calculate_wall_segments()
        
        print(f"\nWall Segment Calculations:")
        print(f"{'Segment':<6} {'Inches':<8} {'Chars':<6} {'Type':<8} {'Symbol'}")
        print("-" * 45)
        
        for segment_id, data in segments.items():
            print(f"{segment_id:<6} {data['inches']:<8.2f} {data['chars']:<6} {data['type']:<8} {data['symbol']}")


def main():
    """Test the layout engine"""
    print("Layout Engine Test")
    print("=" * 40)
    
    engine = LayoutEngine()
    
    # Test at different scales
    print("\n--- Default Scale (1.0) ---")
    engine.current_scale = 1.0
    engine.print_scale_info()
    engine.print_wall_segments_info()
    
    print("\n--- Auto-fit Scale ---")
    auto_scale = engine.auto_scale_to_fit(80, 25)
    print(f"Auto-calculated scale: {auto_scale:.3f}")
    engine.print_scale_info()
    
    print("\n--- Zoom 1.5x ---")
    engine.set_zoom(1.5)
    engine.print_scale_info()
    
    print("\n--- Zoom 0.5x ---")
    engine.set_zoom(0.5)
    engine.print_scale_info()


if __name__ == "__main__":
    main()