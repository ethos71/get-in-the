#!/usr/bin/env python3
"""
Kitchen Scale Converter - Converts ASCII kitchen layouts to real measurements
"""

import json
import math
from typing import Dict, List, Tuple, Any

class KitchenScaleConverter:
    def __init__(self, room_width_feet: float = 12.0, room_height_feet: float = 10.0):
        self.room_width_feet = room_width_feet
        self.room_height_feet = room_height_feet
        self.measurements = {
            "room_dimensions": {
                "width_feet": room_width_feet,
                "height_feet": room_height_feet,
                "width_inches": room_width_feet * 12,
                "height_inches": room_height_feet * 12
            },
            "furniture_dimensions": {
                "table": {"width_feet": 3.0, "height_feet": 2.0, "width_inches": 36, "height_inches": 24},
                "chair": {"width_feet": 1.5, "height_feet": 1.5, "width_inches": 18, "height_inches": 18},
                "fridge": {"width_feet": 3.0, "height_feet": 2.5, "width_inches": 36, "height_inches": 30},
                "stove": {"width_feet": 2.5, "height_feet": 2.0, "width_inches": 30, "height_inches": 24},
                "sink": {"width_feet": 2.0, "height_feet": 1.5, "width_inches": 24, "height_inches": 18},
                "counter": {"width_feet": 2.0, "height_feet": 1.0, "width_inches": 24, "height_inches": 12}
            },
            "clearance_requirements": {
                "walking_space": {"width_feet": 3.0, "width_inches": 36},
                "chair_pullout": {"depth_feet": 2.0, "depth_inches": 24},
                "appliance_clearance": {"width_feet": 3.0, "width_inches": 36}
            }
        }
    
    def feet_to_inches(self, feet: float) -> int:
        """Convert feet to inches"""
        return int(feet * 12)
    
    def inches_to_feet(self, inches: float) -> Tuple[int, int]:
        """Convert inches to feet and remaining inches"""
        feet = int(inches // 12)
        remaining_inches = int(inches % 12)
        return feet, remaining_inches
    
    def format_measurement(self, total_inches: int) -> str:
        """Format measurement as feet'inches\""""
        feet, inches = divmod(total_inches, 12)
        if feet == 0:
            return f"{inches}\""
        elif inches == 0:
            return f"{feet}'"
        else:
            return f"{feet}'{inches}\""
    
    def calculate_ascii_scale(self, ascii_width: int, ascii_height: int) -> Dict[str, float]:
        """Calculate scale factor for ASCII to real world conversion"""
        scale_x = self.room_width_feet / (ascii_width - 2)  # -2 for walls
        scale_y = self.room_height_feet / (ascii_height - 2)  # -2 for walls
        avg_scale = (scale_x + scale_y) / 2
        
        return {
            "scale_x_feet_per_char": scale_x,
            "scale_y_feet_per_char": scale_y,
            "average_scale_feet_per_char": avg_scale,
            "scale_x_inches_per_char": scale_x * 12,
            "scale_y_inches_per_char": scale_y * 12,
            "average_scale_inches_per_char": avg_scale * 12
        }
    
    def calculate_item_position(self, x: int, y: int, scale: Dict[str, float]) -> Dict[str, Any]:
        """Calculate real-world position of an ASCII item"""
        pos_x_feet = (x - 1) * scale["scale_x_feet_per_char"]
        pos_y_feet = (y - 1) * scale["scale_y_feet_per_char"]
        pos_x_inches = pos_x_feet * 12
        pos_y_inches = pos_y_feet * 12
        
        return {
            "position": {"x_char": x, "y_char": y},
            "real_position": {
                "x_feet": round(pos_x_feet, 2),
                "y_feet": round(pos_y_feet, 2),
                "x_inches": round(pos_x_inches, 1),
                "y_inches": round(pos_y_inches, 1)
            }
        }
    
    def analyze_ascii_layout(self, ascii_layout: List[str]) -> Dict[str, Any]:
        """Analyze ASCII layout and convert to real measurements"""
        # Parse ASCII layout
        layout = [list(row) for row in ascii_layout]
        height = len(layout)
        width = len(layout[0])
        
        # Calculate scale
        scale = self.calculate_ascii_scale(width, height)
        
        # Find all furniture positions
        furniture_positions = {}
        furniture_symbols = {
            'T': 'table', 'c': 'chair', 'F': 'fridge', 
            's': 'stove', 'k': 'sink', '-': 'counter'
        }
        
        for y, row in enumerate(layout):
            for x, char in enumerate(row):
                if char in furniture_symbols:
                    furniture_type = furniture_symbols[char]
                    if furniture_type not in furniture_positions:
                        furniture_positions[furniture_type] = []
                    
                    pos_data = self.calculate_item_position(x, y, scale)
                    furniture_positions[furniture_type].append(pos_data)
        
        # Calculate work triangle (fridge-sink-stove)
        work_triangle = self.calculate_work_triangle(furniture_positions, scale)
        
        return {
            "ascii_dimensions": {"width": width, "height": height},
            "scale": scale,
            "furniture_positions": furniture_positions,
            "work_triangle": work_triangle,
            "total_floor_space": self.calculate_total_floor_space(scale)
        }
    
    def calculate_work_triangle(self, furniture_positions: Dict[str, List[Dict]], 
                              scale: Dict[str, float]) -> Dict[str, Any]:
        """Calculate the work triangle between fridge, sink, and stove"""
        fridge_pos = furniture_positions.get('fridge', [])
        sink_pos = furniture_positions.get('sink', [])
        stove_pos = furniture_positions.get('stove', [])
        
        if not all([fridge_pos, sink_pos, stove_pos]):
            return {"error": "Missing one or more work stations"}
        
        # Use first occurrence of each
        fridge = fridge_pos[0]["real_position"]
        sink = sink_pos[0]["real_position"]
        stove = stove_pos[0]["real_position"]
        
        def calculate_distance(pos1, pos2):
            dx = pos1["x_feet"] - pos2["x_feet"]
            dy = pos1["y_feet"] - pos2["y_feet"]
            return math.sqrt(dx**2 + dy**2)
        
        fridge_to_sink = calculate_distance(fridge, sink)
        sink_to_stove = calculate_distance(sink, stove)
        stove_to_fridge = calculate_distance(stove, fridge)
        total_perimeter = fridge_to_sink + sink_to_stove + stove_to_fridge
        
        return {
            "distances_feet": {
                "fridge_to_sink": round(fridge_to_sink, 2),
                "sink_to_stove": round(sink_to_stove, 2),
                "stove_to_fridge": round(stove_to_fridge, 2),
                "total_perimeter": round(total_perimeter, 2)
            },
            "distances_inches": {
                "fridge_to_sink": round(fridge_to_sink * 12, 1),
                "sink_to_stove": round(sink_to_stove * 12, 1),
                "stove_to_fridge": round(stove_to_fridge * 12, 1),
                "total_perimeter": round(total_perimeter * 12, 1)
            },
            "is_optimal": 10 <= total_perimeter <= 25  # Optimal work triangle is 10-25 feet
        }
    
    def calculate_total_floor_space(self, scale: Dict[str, float]) -> Dict[str, Any]:
        """Calculate total usable floor space"""
        usable_width_feet = (self.room_width_feet - 1)  # Subtract 1 foot for walls
        usable_height_feet = (self.room_height_feet - 1)  # Subtract 1 foot for walls
        total_area_feet2 = usable_width_feet * usable_height_feet
        total_area_inches2 = total_area_feet2 * 144  # 144 square inches per square foot
        
        return {
            "usable_dimensions_feet": {
                "width": usable_width_feet,
                "height": usable_height_feet
            },
            "usable_dimensions_inches": {
                "width": usable_width_feet * 12,
                "height": usable_height_feet * 12
            },
            "total_area_feet2": round(total_area_feet2, 1),
            "total_area_inches2": round(total_area_inches2, 1)
        }
    
    def save_measurements_to_json(self, filename: str = "kitchen_measurements.json"):
        """Save all measurements to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.measurements, f, indent=2)
        print(f"Measurements saved to {filename}")
    
    def load_measurements_from_json(self, filename: str = "kitchen_measurements.json") -> Dict[str, Any]:
        """Load measurements from JSON file"""
        try:
            with open(filename, 'r') as f:
                self.measurements = json.load(f)
            print(f"Measurements loaded from {filename}")
            return self.measurements
        except FileNotFoundError:
            print(f"File {filename} not found. Using default measurements.")
            return self.measurements
    
    def generate_measurement_report(self, analysis: Dict[str, Any]) -> str:
        """Generate a detailed measurement report"""
        report = []
        report.append("KITCHEN MEASUREMENT REPORT")
        report.append("=" * 50)
        
        # Room dimensions
        room = self.measurements["room_dimensions"]
        report.append(f"Room: {self.format_measurement(room['width_inches'])} × {self.format_measurement(room['height_inches'])}")
        
        # Scale information
        scale = analysis["scale"]
        report.append(f"\nScale: 1 char = {self.format_measurement(int(scale['average_scale_inches_per_char']))}")
        
        # Furniture items
        report.append("\nFurniture Positions:")
        for furniture_type, positions in analysis["furniture_positions"].items():
            dims = self.measurements["furniture_dimensions"][furniture_type]
            report.append(f"  {furniture_type.capitalize()}: {self.format_measurement(dims['width_inches'])} × {self.format_measurement(dims['height_inches'])}")
            for i, pos in enumerate(positions[:3], 1):  # Show max 3 positions
                real_pos = pos["real_position"]
                report.append(f"    Position {i}: ({self.format_measurement(int(real_pos['x_inches']))}, {self.format_measurement(int(real_pos['y_inches']))})")
        
        # Work triangle
        if "distances_feet" in analysis["work_triangle"]:
            report.append("\nWork Triangle:")
            wt = analysis["work_triangle"]["distances_feet"]
            report.append(f"  Fridge to Sink: {self.format_measurement(int(wt['fridge_to_sink'] * 12))}")
            report.append(f"  Sink to Stove: {self.format_measurement(int(wt['sink_to_stove'] * 12))}")
            report.append(f"  Stove to Fridge: {self.format_measurement(int(wt['stove_to_fridge'] * 12))}")
            report.append(f"  Total Perimeter: {self.format_measurement(int(wt['total_perimeter'] * 12))}")
            report.append(f"  Optimal: {'Yes' if analysis['work_triangle']['is_optimal'] else 'No'}")
        
        # Floor space
        floor = analysis["total_floor_space"]
        report.append(f"\nUsable Floor Space: {floor['total_area_feet2']} ft²")
        
        return "\n".join(report)


def main():
    """Main function to demonstrate the converter"""
    # Example ASCII kitchen layout
    example_layout = [
        "###########=|############",
        "#                       #",
        "# --------------------- #",
        "#                       #",
        "#                       #",
        "#                       #",
        "#                       #",
        "           c           ",
        "          cTc          ",
        "           c           ",
        "                       #",
        "#########################"
    ]
    
    converter = KitchenScaleConverter(room_width_feet=12.0, room_height_feet=10.0)
    
    # Save measurements to JSON
    converter.save_measurements_to_json()
    
    # Analyze layout
    analysis = converter.analyze_ascii_layout(example_layout)
    
    # Generate report
    report = converter.generate_measurement_report(analysis)
    print(report)
    
    # Save analysis to JSON
    with open("kitchen_analysis.json", 'w') as f:
        json.dump(analysis, f, indent=2)
    print("\nAnalysis saved to kitchen_analysis.json")


if __name__ == "__main__":
    main()