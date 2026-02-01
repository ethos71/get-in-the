#!/usr/bin/env python3
"""
SVG Renderer - Generates accurate SVG floor plans from measurements
"""

import svgwrite
from typing import Dict, Tuple
import json
import sys
import os

class SVGRenderer:
    def __init__(self, config_path: str = "scripts/config/kitchen_measurements.json", scale: float = 2.0):
        """
        Initialize SVG renderer
        
        Args:
            config_path: Path to kitchen measurements config
            scale: SVG scale factor (pixels per inch)
        """
        self.config_path = config_path
        self.measurements = self.load_measurements()
        self.scale = scale  # pixels per inch
        
        # Colors and styles
        self.wall_color = '#000000'
        self.wall_width = 3
        self.door_color = '#8B4513'
        self.door_width = 2
        self.window_color = '#4169E1'
        self.window_width = 2
        self.floor_color = '#F5F5DC'
        self.text_color = '#333333'
        self.dimension_color = '#666666'
        
    def load_measurements(self) -> Dict:
        """Load measurements from config file"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: Config file {self.config_path} not found")
            sys.exit(1)
    
    def inches_to_pixels(self, inches: float) -> float:
        """Convert inches to SVG pixels"""
        return inches * self.scale
    
    def create_kitchen_layout(self, output_path: str = "output/kitchen_layout.svg"):
        """
        Create SVG kitchen layout with accurate measurements
        """
        wall_measurements = self.measurements.get("wall_measurements", {})
        
        # Calculate north wall width
        north_width = wall_measurements["N1"]["measurement_inches"] + wall_measurements["N2"]["measurement_inches"]
        west_height = (wall_measurements["W1"]["measurement_inches"] + 
                      wall_measurements["W2"]["measurement_inches"] + 
                      wall_measurements["W3"]["measurement_inches"])
        
        # Calculate additional space needed for north alcove
        north_alcove_depth = 0
        if "segments" in wall_measurements["N2"]:
            import math
            # Calculate how far north the alcove extends
            for seg in wall_measurements["N2"]["segments"]:
                direction = seg.get("direction", "E")
                seg_inches = seg["measurement_inches"]
                if direction == "N":
                    north_alcove_depth += seg_inches
                elif direction == "NE":
                    # NE contributes to northern extension
                    north_alcove_depth += seg_inches * math.sin(math.radians(45))
        
        # Convert to pixels and add margins
        margin = 50  # pixels
        svg_width = self.inches_to_pixels(north_width) + (margin * 2)
        # Add extra space for north alcove
        svg_height = self.inches_to_pixels(west_height) + self.inches_to_pixels(north_alcove_depth) + (margin * 2) + 40
        
        # Create SVG drawing
        dwg = svgwrite.Drawing(output_path, size=(f"{svg_width}px", f"{svg_height}px"))
        
        # Add background
        dwg.add(dwg.rect(insert=(0, 0), size=(svg_width, svg_height), fill='white'))
        
        # Create main group with margin offset - shift down to accommodate north alcove
        y_offset = margin + self.inches_to_pixels(north_alcove_depth)
        main_group = dwg.g(transform=f"translate({margin},{y_offset})")
        
        # Add floor background for the L-shaped room with north alcove
        floor_group = dwg.g()
        
        # Calculate L-shape dimensions
        south_wall_length = (wall_measurements["S1"]["measurement_inches"] + 
                            wall_measurements["S2"]["measurement_inches"] + 
                            wall_measurements["S3"]["measurement_inches"])
        alcove_depth = wall_measurements["E1"]["measurement_inches"]
        
        # Main rectangle (north width x west height)
        main_rect_width = self.inches_to_pixels(north_width)
        main_rect_height = self.inches_to_pixels(west_height)
        
        # South alcove dimensions
        south_wall_px = self.inches_to_pixels(south_wall_length)
        alcove_depth_px = self.inches_to_pixels(alcove_depth)
        e2_width_px = self.inches_to_pixels(wall_measurements["E2"]["measurement_inches"])
        e3_height_px = self.inches_to_pixels(wall_measurements["E3"]["measurement_inches"])
        
        # North alcove dimensions (if N2 has segments)
        n1_width_px = self.inches_to_pixels(wall_measurements["N1"]["measurement_inches"])
        
        # Build path for floor plan with both alcoves
        path_points = []
        
        # Start at top-left, trace clockwise
        path_points.append(f"M 0 0")  # Top-left corner
        path_points.append(f"L {n1_width_px} 0")  # N1 wall
        
        # N2 alcove (if it has segments)
        if "segments" in wall_measurements["N2"]:
            import math
            x = n1_width_px
            y = 0
            for seg in wall_measurements["N2"]["segments"]:
                seg_length = self.inches_to_pixels(seg["measurement_inches"])
                direction = seg.get("direction", "E")
                
                if direction == "N":
                    y -= seg_length
                elif direction == "NE":
                    x += seg_length * math.cos(math.radians(45))
                    y -= seg_length * math.sin(math.radians(45))
                elif direction == "E":
                    x += seg_length
                elif direction == "SE":
                    x += seg_length * math.cos(math.radians(-45))
                    y += seg_length * math.sin(math.radians(-45))
                
                path_points.append(f"L {x} {y}")
        else:
            path_points.append(f"L {main_rect_width} 0")  # Straight north wall
        
        # Continue with rest of room
        path_points.append(f"L {main_rect_width} {e3_height_px}")  # E3 down
        path_points.append(f"L {south_wall_px} {e3_height_px}")  # E2 left (south alcove top)
        path_points.append(f"L {south_wall_px} {main_rect_height}")  # E1 down (south alcove right)
        path_points.append(f"L 0 {main_rect_height}")  # South wall left
        path_points.append(f"Z")  # Close path (West wall up)
        
        floor_group.add(dwg.path(
            d=" ".join(path_points),
            fill=self.floor_color,
            stroke='none'
        ))
        
        main_group.add(floor_group)
        
        # Draw walls
        walls_group = dwg.g()
        
        # North wall
        y_pos = 0
        x_pos = 0
        
        # N1 - wall segment
        n1_width = self.inches_to_pixels(wall_measurements["N1"]["measurement_inches"])
        walls_group.add(dwg.line(
            start=(x_pos, y_pos),
            end=(x_pos + n1_width, y_pos),
            stroke=self.wall_color,
            stroke_width=self.wall_width
        ))
        self._add_dimension(dwg, walls_group, x_pos, y_pos - 20, x_pos + n1_width, y_pos - 20, 
                           f'N1: {wall_measurements["N1"]["measurement_inches"]}"')
        x_pos += n1_width
        
        # N2 - alcove (not a window)
        n2_total = wall_measurements["N2"]["measurement_inches"]
        
        if "segments" in wall_measurements["N2"]:
            # Draw alcove segments with angles
            import math
            
            segments = wall_measurements["N2"]["segments"]
            start_x = x_pos
            start_y = y_pos
            
            for seg in segments:
                seg_length = self.inches_to_pixels(seg["measurement_inches"])
                direction = seg.get("direction", "E")
                
                # Calculate end point based on direction
                if direction == "N":
                    end_x = start_x
                    end_y = start_y - seg_length
                elif direction == "NE":
                    # 45 degree angle northeast
                    end_x = start_x + seg_length * math.cos(math.radians(45))
                    end_y = start_y - seg_length * math.sin(math.radians(45))
                elif direction == "E":
                    end_x = start_x + seg_length
                    end_y = start_y
                elif direction == "SE":
                    # 45 degree angle southeast
                    end_x = start_x + seg_length * math.cos(math.radians(-45))
                    end_y = start_y + seg_length * math.sin(math.radians(-45))
                else:
                    end_x = start_x + seg_length
                    end_y = start_y
                
                # Draw wall segment
                walls_group.add(dwg.line(
                    start=(start_x, start_y),
                    end=(end_x, end_y),
                    stroke=self.wall_color,
                    stroke_width=self.wall_width
                ))
                
                start_x = end_x
                start_y = end_y
            
            # Update x_pos to end of alcove (should be 86" from start)
            x_pos += self.inches_to_pixels(n2_total)
            
            # Dimension label for N2
            self._add_dimension(dwg, walls_group, x_pos - self.inches_to_pixels(n2_total), y_pos - 30, 
                               x_pos, y_pos - 30, f'N2: {n2_total}" (alcove)')
        else:
            # Fallback: draw as simple wall
            n2_width = self.inches_to_pixels(n2_total)
            walls_group.add(dwg.line(
                start=(x_pos, y_pos),
                end=(x_pos + n2_width, y_pos),
                stroke=self.wall_color,
                stroke_width=self.wall_width
            ))
            self._add_dimension(dwg, walls_group, x_pos, y_pos - 20, x_pos + n2_width, y_pos - 20, 
                               f'N2: {n2_total}"')
            x_pos += n2_width
        
        # West wall (going down from top-left)
        x_pos = 0
        y_pos = 0
        
        # W1 - wall segment
        w1_height = self.inches_to_pixels(wall_measurements["W1"]["measurement_inches"])
        walls_group.add(dwg.line(
            start=(x_pos, y_pos),
            end=(x_pos, y_pos + w1_height),
            stroke=self.wall_color,
            stroke_width=self.wall_width
        ))
        self._add_dimension(dwg, walls_group, x_pos - 20, y_pos, x_pos - 20, y_pos + w1_height,
                           f'W1: {wall_measurements["W1"]["measurement_inches"]}"', vertical=True)
        y_pos += w1_height
        
        # W2 - door
        w2_height = self.inches_to_pixels(wall_measurements["W2"]["measurement_inches"])
        walls_group.add(dwg.line(
            start=(x_pos, y_pos),
            end=(x_pos, y_pos + w2_height),
            stroke=self.door_color,
            stroke_width=self.door_width
        ))
        # Door arc
        walls_group.add(dwg.path(
            d=f"M {x_pos} {y_pos} Q {x_pos + w2_height} {y_pos} {x_pos} {y_pos + w2_height}",
            stroke=self.door_color,
            stroke_width=1,
            fill='none',
            stroke_dasharray="5,3"
        ))
        self._add_dimension(dwg, walls_group, x_pos - 20, y_pos, x_pos - 20, y_pos + w2_height,
                           f'W2: {wall_measurements["W2"]["measurement_inches"]}" (door)', vertical=True)
        y_pos += w2_height
        
        # W3 - wall segment
        w3_height = self.inches_to_pixels(wall_measurements["W3"]["measurement_inches"])
        walls_group.add(dwg.line(
            start=(x_pos, y_pos),
            end=(x_pos, y_pos + w3_height),
            stroke=self.wall_color,
            stroke_width=self.wall_width
        ))
        self._add_dimension(dwg, walls_group, x_pos - 20, y_pos, x_pos - 20, y_pos + w3_height,
                           f'W3: {wall_measurements["W3"]["measurement_inches"]}"', vertical=True)
        y_pos += w3_height
        
        # South wall (going right from bottom-left)
        x_pos = 0
        y_pos = self.inches_to_pixels(west_height)
        
        # S1 - wall segment
        s1_width = self.inches_to_pixels(wall_measurements["S1"]["measurement_inches"])
        walls_group.add(dwg.line(
            start=(x_pos, y_pos),
            end=(x_pos + s1_width, y_pos),
            stroke=self.wall_color,
            stroke_width=self.wall_width
        ))
        self._add_dimension(dwg, walls_group, x_pos, y_pos + 20, x_pos + s1_width, y_pos + 20,
                           f'S1: {wall_measurements["S1"]["measurement_inches"]}"')
        x_pos += s1_width
        
        # S2 - door
        s2_width = self.inches_to_pixels(wall_measurements["S2"]["measurement_inches"])
        walls_group.add(dwg.line(
            start=(x_pos, y_pos),
            end=(x_pos + s2_width, y_pos),
            stroke=self.door_color,
            stroke_width=self.door_width
        ))
        # Door arc
        walls_group.add(dwg.path(
            d=f"M {x_pos} {y_pos} Q {x_pos} {y_pos - s2_width} {x_pos + s2_width} {y_pos}",
            stroke=self.door_color,
            stroke_width=1,
            fill='none',
            stroke_dasharray="5,3"
        ))
        self._add_dimension(dwg, walls_group, x_pos, y_pos + 20, x_pos + s2_width, y_pos + 20,
                           f'S2: {wall_measurements["S2"]["measurement_inches"]}" (door)')
        x_pos += s2_width
        
        # S3 - wall segment
        s3_width = self.inches_to_pixels(wall_measurements["S3"]["measurement_inches"])
        walls_group.add(dwg.line(
            start=(x_pos, y_pos),
            end=(x_pos + s3_width, y_pos),
            stroke=self.wall_color,
            stroke_width=self.wall_width
        ))
        self._add_dimension(dwg, walls_group, x_pos, y_pos + 20, x_pos + s3_width, y_pos + 20,
                           f'S3: {wall_measurements["S3"]["measurement_inches"]}"')
        
        # East wall segments (creating the L-shape alcove)
        # E3 - top segment (from top-right going down)
        east_x = self.inches_to_pixels(north_width)
        e3_height = self.inches_to_pixels(wall_measurements["E3"]["measurement_inches"])
        walls_group.add(dwg.line(
            start=(east_x, 0),
            end=(east_x, e3_height),
            stroke=self.wall_color,
            stroke_width=self.wall_width
        ))
        self._add_dimension(dwg, walls_group, east_x + 20, 0, east_x + 20, e3_height,
                           f'E3: {wall_measurements["E3"]["measurement_inches"]}"', vertical=True)
        
        # E2 - horizontal segment (alcove top) - goes from south wall end to east wall
        south_wall_end_x = self.inches_to_pixels(south_wall_length)
        e2_total = wall_measurements["E2"]["measurement_inches"]
        
        # Check if E2 has sub-segments (door)
        if "segments" in wall_measurements["E2"]:
            x_pos = south_wall_end_x
            for segment in wall_measurements["E2"]["segments"]:
                seg_width = self.inches_to_pixels(segment["measurement_inches"])
                if segment["type"] == "door":
                    # Draw door
                    walls_group.add(dwg.line(
                        start=(x_pos, e3_height),
                        end=(x_pos + seg_width, e3_height),
                        stroke=self.door_color,
                        stroke_width=self.door_width
                    ))
                    # Door arc (opens upward)
                    walls_group.add(dwg.path(
                        d=f"M {x_pos} {e3_height} Q {x_pos + seg_width/2} {e3_height - seg_width} {x_pos + seg_width} {e3_height}",
                        stroke=self.door_color,
                        stroke_width=1,
                        fill='none',
                        stroke_dasharray="5,3"
                    ))
                else:
                    # Draw wall segment
                    walls_group.add(dwg.line(
                        start=(x_pos, e3_height),
                        end=(x_pos + seg_width, e3_height),
                        stroke=self.wall_color,
                        stroke_width=self.wall_width
                    ))
                x_pos += seg_width
        else:
            # No sub-segments, draw as single wall
            e2_width = self.inches_to_pixels(e2_total)
            walls_group.add(dwg.line(
                start=(south_wall_end_x, e3_height),
                end=(east_x, e3_height),
                stroke=self.wall_color,
                stroke_width=self.wall_width
            ))
        
        # Dimension label for E2
        self._add_dimension(dwg, walls_group, south_wall_end_x, e3_height - 20, east_x, e3_height - 20,
                           f'E2: {e2_total}"')
        
        # E1 - alcove right side (from alcove top down to south wall)
        e1_height = self.inches_to_pixels(wall_measurements["E1"]["measurement_inches"])
        walls_group.add(dwg.line(
            start=(south_wall_end_x, e3_height),
            end=(south_wall_end_x, e3_height + e1_height),
            stroke=self.wall_color,
            stroke_width=self.wall_width
        ))
        self._add_dimension(dwg, walls_group, south_wall_end_x + 20, e3_height, south_wall_end_x + 20, e3_height + e1_height,
                           f'E1: {wall_measurements["E1"]["measurement_inches"]}"', vertical=True)
        
        main_group.add(walls_group)
        
        # Add title
        title = dwg.text('Kitchen Layout', 
                        insert=(self.inches_to_pixels(north_width) / 2, -30),
                        text_anchor='middle',
                        font_size='20px',
                        font_family='Arial',
                        fill=self.text_color,
                        font_weight='bold')
        main_group.add(title)
        
        # Add scale info
        scale_text = dwg.text(f'Scale: {self.scale} pixels/inch', 
                             insert=(5, self.inches_to_pixels(west_height) + 40),
                             font_size='12px',
                             font_family='Arial',
                             fill=self.dimension_color)
        main_group.add(scale_text)
        
        # Add compass
        self._add_compass(dwg, main_group, self.inches_to_pixels(north_width) - 50, 50)
        
        dwg.add(main_group)
        
        # Save the file
        dwg.save()
        print(f"✅ SVG layout saved to: {output_path}")
        print(f"   Dimensions: {svg_width:.0f}px x {svg_height:.0f}px")
        print(f"   Scale: {self.scale} pixels/inch")
        
    def _add_dimension(self, dwg, group, x1, y1, x2, y2, label, vertical=False):
        """Add dimension line with label"""
        # Dimension line
        group.add(dwg.line(
            start=(x1, y1),
            end=(x2, y2),
            stroke=self.dimension_color,
            stroke_width=0.5
        ))
        
        # End markers
        marker_size = 3
        group.add(dwg.line(
            start=(x1, y1 - marker_size),
            end=(x1, y1 + marker_size),
            stroke=self.dimension_color,
            stroke_width=0.5
        ))
        group.add(dwg.line(
            start=(x2, y2 - marker_size),
            end=(x2, y2 + marker_size),
            stroke=self.dimension_color,
            stroke_width=0.5
        ))
        
        # Label
        label_x = (x1 + x2) / 2
        label_y = (y1 + y2) / 2
        
        text = dwg.text(label,
                       insert=(label_x, label_y - 3 if not vertical else label_y),
                       text_anchor='middle',
                       font_size='10px',
                       font_family='Arial',
                       fill=self.dimension_color)
        
        if vertical:
            text['transform'] = f"rotate(-90 {label_x} {label_y})"
        
        group.add(text)
    
    def _add_compass(self, dwg, group, x, y):
        """Add north compass indicator"""
        compass = dwg.g()
        
        # North arrow
        compass.add(dwg.line(
            start=(x, y),
            end=(x, y - 30),
            stroke=self.text_color,
            stroke_width=2
        ))
        compass.add(dwg.polygon(
            points=[(x, y - 30), (x - 5, y - 20), (x + 5, y - 20)],
            fill=self.text_color
        ))
        
        # N label
        compass.add(dwg.text('N',
                            insert=(x, y - 35),
                            text_anchor='middle',
                            font_size='14px',
                            font_family='Arial',
                            fill=self.text_color,
                            font_weight='bold'))
        
        group.add(compass)


if __name__ == "__main__":
    renderer = SVGRenderer(scale=3.0)
    renderer.create_kitchen_layout()
