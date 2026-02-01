#!/usr/bin/env python3
"""
Kitchen Layout Generator - Creates ASCII kitchen layouts matching the exact specification
"""

import json
import sys
import os
from typing import List, Tuple, Dict

class KitchenLayoutGenerator:
    def __init__(self, config_path: str = "scripts/config/kitchen_measurements.json"):
        self.config_path = config_path
        self.config = self.load_config()
        
        # Get the layout from config
        self.layout_template = self.config.get("layout_ascii", [])
        
        self.furniture_symbols = {
            'table': 'T',
            'chair': 'c',
            'fridge': 'F',
            'stove': 's',
            'sink': 'k',
            'counter': '-',
            'door': '|',
            'window': '=',
            'wall': '#',
            'floor': ' '
        }
    
    def load_config(self) -> Dict:
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: Config file {self.config_path} not found")
            sys.exit(1)
    
    def get_base_layout(self) -> List[List[str]]:
        """Get the base kitchen layout from template"""
        layout = []
        for line in self.layout_template:
            layout.append(list(line))
        return layout
    
    def place_furniture(self, layout: List[List[str]], furniture_type: str, 
                       x: int, y: int) -> List[List[str]]:
        """Place furniture in the room at specific coordinates"""
        symbol = self.furniture_symbols.get(furniture_type, '?')
        
        if (0 <= y < len(layout) and 0 <= x < len(layout[y]) and 
            layout[y][x] == self.furniture_symbols['floor']):
            layout[y][x] = symbol
        
        return layout
    
    def layout_to_string(self, layout: List[List[str]]) -> str:
        """Convert layout to string"""
        return '\n'.join([''.join(row) for row in layout])
    
    def print_legend(self):
        """Print the legend"""
        print("\nLegend:")
        items = [
            ('T', 'Table'),
            ('c', 'Chair'),
            ('F', 'Fridge'),
            ('s', 'Stove'),
            ('k', 'Sink'),
            ('-', 'Counter'),
            ('|', 'Door'),
            ('=', 'Window'),
            ('#', 'Wall')
        ]
        for symbol, name in items:
            print(f"  {symbol}: {name}")
        
        print("\nWall Labels:")
        print("  N: North Wall")
        print("  S: South Wall")
        print("  E: East Wall")
        print("  W: West Wall")
    
    def print_measurements(self):
        """Print wall measurements"""
        print("\nWall Measurements:")
        
        wall_measurements = self.config.get("wall_measurements", {})
        
        # Sort by wall orientation and segment
        order = ["N1", "N2", "W1", "W2", "W3", "S1", "S2", "S3", "E1", "E2", "E3"]
        
        for segment_id in order:
            if segment_id in wall_measurements:
                data = wall_measurements[segment_id]
                symbol = data["symbol"]
                inches = data["measurement_inches"]
                seg_type = data["type"]
                print(f"{symbol}{segment_id} = {inches}\" ({seg_type})")
    
    def generate_kitchen(self) -> List[List[str]]:
        """Generate the kitchen layout"""
        return self.get_base_layout()
    
    def analyze_layout(self):
        """Analyze and print layout information"""
        layout = self.get_base_layout()
        
        print("\nLayout Analysis:")
        print(f"  Height: {len(layout)} lines")
        print(f"  Width: {max(len(row) for row in layout)} characters")
        
        # Count wall segments
        wall_measurements = self.config.get("wall_measurements", {})
        print(f"  Total wall segments: {len(wall_measurements)}")
        
        # Calculate total perimeter
        total_inches = sum(data["measurement_inches"] for data in wall_measurements.values())
        total_feet = total_inches / 12
        print(f"  Total wall length: {total_inches}\" ({total_feet:.2f}')")


def main():
    """Main function to generate kitchen layouts"""
    print("Kitchen Layout Generator")
    print("=" * 50)
    
    # Create generator
    generator = KitchenLayoutGenerator()
    
    # Generate and display kitchen layout
    layout = generator.generate_kitchen()
    print("\nKitchen Layout:")
    print(generator.layout_to_string(layout))
    
    # Print legend and measurements
    generator.print_legend()
    generator.print_measurements()
    
    # Print analysis
    generator.analyze_layout()


if __name__ == "__main__":
    main()
