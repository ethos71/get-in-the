#!/usr/bin/env python3
"""
Kitchen Layout Generator - Creates proportionally accurate ASCII layouts
"""

import json
import sys
import os
from typing import List, Tuple, Dict

# Add the engine directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'engine'))
from layout_scaling_engine import LayoutEngine

class KitchenLayoutGenerator:
    def __init__(self, config_path: str = "scripts/config/kitchen_measurements.json", zoom: float = 1.0):
        self.config_path = config_path
        self.config = self.load_config()
        self.zoom = zoom
        self.engine = LayoutEngine(config_path)
        
        self.symbols = {
            'wall': '#',
            'door': '|',
            'window': '=',
            'floor': ' '
        }
    
    def load_config(self) -> Dict:
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: Config file {self.config_path} not found")
            sys.exit(1)
    
    def create_proportional_layout(self, max_width: int = 80, max_height: int = 30) -> List[List[str]]:
        """
        Create proportionally accurate L-shaped kitchen
        Based on real measurements with proper scaling
        """
        # Set up scaling
        self.engine.auto_scale_to_fit(max_width, max_height)
        self.engine.set_zoom(self.zoom)
        
        # Get scaled wall segments
        segments = self.engine.calculate_wall_segments()
        
        # Calculate wall lengths in characters
        n1 = segments.get("N1", {}).get("chars", 0)
        n2 = segments.get("N2", {}).get("chars", 0)
        w1 = segments.get("W1", {}).get("chars", 0)
        w2 = segments.get("W2", {}).get("chars", 0)
        w3 = segments.get("W3", {}).get("chars", 0)
        s1 = segments.get("S1", {}).get("chars", 0)
        s2 = segments.get("S2", {}).get("chars", 0)
        s3 = segments.get("S3", {}).get("chars", 0)
        e1 = segments.get("E1", {}).get("chars", 0)
        e2 = segments.get("E2", {}).get("chars", 0)
        e3 = segments.get("E3", {}).get("chars", 0)
        
        # Total dimensions
        north_total = n1 + n2  # Full width at top
        west_total = w1 + w2 + w3  # Full height on left
        south_total = s1 + s2 + s3  # Shorter bottom
        
        # Canvas size: north width × west height (main room)
        width = north_total
        height = west_total
        
        # Initialize with floor
        layout = [[' ' for _ in range(width)] for _ in range(height)]
        
        # === NORTH WALL (top) ===
        x = 0
        # N1 - wall segment
        for i in range(n1):
            if x < width:
                layout[0][x] = '#'
                x += 1
        # N2 - window
        for i in range(n2):
            if x < width:
                layout[0][x] = '='
                x += 1
        
        # === WEST WALL (left) ===
        y = 0
        # W1 - wall
        for i in range(w1):
            if y < height:
                layout[y][0] = '#'
                y += 1
        # W2 - door
        for i in range(w2):
            if y < height:
                layout[y][0] = '|'
                y += 1
        # W3 - wall
        for i in range(w3):
            if y < height:
                layout[y][0] = '#'
                y += 1
        
        # === SOUTH WALL (bottom, short) ===
        x = 0
        # S1 - wall
        for i in range(s1):
            if x < width:
                layout[height-1][x] = '#'
                x += 1
        # S2 - door
        for i in range(s2):
            if x < width:
                layout[height-1][x] = '|'
                x += 1
        # S3 - wall
        for i in range(s3):
            if x < width:
                layout[height-1][x] = '#'
                x += 1
        # x now points to where south wall ends (start of alcove)
        south_end_x = x
        
        # === EAST WALL (right, complex with alcove) ===
        # E3 goes down the right edge from top
        for y in range(e3):
            if y < height:
                layout[y][width-1] = '#'
        
        # After E3, alcove begins
        alcove_top_y = e3
        
        # E2 creates the alcove:
        # - Horizontal wall from where south ends to right edge
        # - Vertical wall down from there
        if alcove_top_y < height:
            # Horizontal part (top of alcove)
            for x in range(south_end_x, width):
                layout[alcove_top_y][x] = '#'
            
            # Vertical part (left side of alcove going down)
            for y in range(alcove_top_y + 1, min(alcove_top_y + e2, height)):
                layout[y][south_end_x] = '#'
        
        # E1 continues down inside the alcove
        e1_start_y = alcove_top_y + e2
        for y in range(e1_start_y, min(e1_start_y + e1, height)):
            if south_end_x < width:
                layout[y][south_end_x] = '#'
        
        return layout
    
    def add_compass_labels(self, layout: List[List[str]]) -> List[str]:
        """Add N/S/E/W compass labels"""
        width = len(layout[0]) if layout else 0
        result = []
        
        # North label
        result.append(" " * (width // 2) + "N")
        
        # Layout with W/E labels
        for i, row in enumerate(layout):
            row_str = ''.join(row)
            if i == len(layout) // 2:
                result.append(f"W {row_str} E")
            else:
                result.append(f"  {row_str}")
        
        # South label
        result.append(" " * (width // 2) + "S")
        
        return result
    
    def layout_to_string(self, layout: List[List[str]]) -> str:
        labeled = self.add_compass_labels(layout)
        return '\n'.join(labeled)
    
    def print_info(self):
        """Print measurement and scale information"""
        measurements = self.config.get("wall_measurements", {})
        segments = self.engine.calculate_wall_segments()
        
        print(f"\n{'='*60}")
        print("Scale Information:")
        print(f"{'='*60}")
        self.engine.print_scale_info()
        
        # Calculate totals
        north = measurements['N1']['measurement_inches'] + measurements['N2']['measurement_inches']
        west = measurements['W1']['measurement_inches'] + measurements['W2']['measurement_inches'] + measurements['W3']['measurement_inches']
        south = measurements['S1']['measurement_inches'] + measurements['S2']['measurement_inches'] + measurements['S3']['measurement_inches']
        east = measurements['E1']['measurement_inches'] + measurements['E2']['measurement_inches'] + measurements['E3']['measurement_inches']
        
        n_chars = sum(segments[s]["chars"] for s in ["N1", "N2"] if s in segments)
        w_chars = sum(segments[s]["chars"] for s in ["W1", "W2", "W3"] if s in segments)
        s_chars = sum(segments[s]["chars"] for s in ["S1", "S2", "S3"] if s in segments)
        
        print(f"\n{'='*60}")
        print("Wall Totals:")
        print(f"{'='*60}")
        print(f"  North: {north}\" → {n_chars} chars")
        print(f"  West:  {west}\" → {w_chars} chars")
        print(f"  South: {south}\" → {s_chars} chars (SHORT - creates L)")
        print(f"  East:  {east}\"")
        print(f"\nProportions:")
        print(f"  Aspect ratio (N/W): {n_chars}/{w_chars} = {n_chars/w_chars:.2f}")
        print(f"  Expected ratio: {north/west:.2f}")
        print(f"  Match: {'✅ CORRECT' if abs(n_chars/w_chars - north/west) < 0.1 else '❌ OFF'}")
        
        print(f"\n{'='*60}")
        print("Wall Measurements:")
        print(f"{'='*60}")
        walls = {
            "North": ["N1", "N2"],
            "West": ["W1", "W2", "W3"],
            "South": ["S1", "S2", "S3"],
            "East": ["E1", "E2", "E3"]
        }
        
        for wall_name, segs in walls.items():
            print(f"  {wall_name}:")
            for seg in segs:
                if seg in measurements:
                    d = measurements[seg]
                    print(f"    {d['symbol']}{seg} = {d['measurement_inches']}\" ({d['type']})")
    
    def generate_kitchen(self, max_width: int = 80, max_height: int = 30) -> List[List[str]]:
        return self.create_proportional_layout(max_width, max_height)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate proportionally accurate kitchen layouts')
    parser.add_argument('--zoom', type=float, default=1.0, help='Zoom level (0.5-2.0)')
    parser.add_argument('--width', type=int, default=80, help='Max width in characters')
    parser.add_argument('--height', type=int, default=30, help='Max height in characters')
    
    args = parser.parse_args()
    
    print("Kitchen Layout Generator - Proportionally Accurate")
    print("=" * 60)
    
    generator = KitchenLayoutGenerator(zoom=args.zoom)
    layout = generator.generate_kitchen(max_width=args.width, max_height=args.height)
    
    print("\nProportionally Accurate Kitchen Layout:")
    print(generator.layout_to_string(layout))
    
    generator.print_info()
    
    print(f"\n{'='*60}")
    print("Usage:")
    print(f"{'='*60}")
    print("  python3 scripts/kitchen_layout_generator.py")
    print("  python3 scripts/kitchen_layout_generator.py --zoom 0.5")
    print("  python3 scripts/kitchen_layout_generator.py --zoom 1.5")
    print("  python3 scripts/kitchen_layout_generator.py --width 120 --height 50")


if __name__ == "__main__":
    main()
