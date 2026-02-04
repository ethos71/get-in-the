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
        Create SVG kitchen layout with accurate measurements - side-by-side view
        Left: Wall Cabinets, Right: Base Cabinets
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
        layout_width = self.inches_to_pixels(north_width) + (margin * 2)
        layout_height = self.inches_to_pixels(west_height) + self.inches_to_pixels(north_alcove_depth) + (margin * 2) + 40
        
        # Create side-by-side layout: Wall cabinets (left) + Base cabinets (right) + Legend + Shopping List
        gap_between = 80  # pixels between the two layouts
        legend_width = 150  # pixels for legend
        legend_gap = 40  # gap before legend
        shopping_list_width = 200  # pixels for shopping list
        shopping_list_gap = 30  # gap before shopping list
        svg_width = (layout_width * 2) + gap_between + legend_gap + legend_width + shopping_list_gap + shopping_list_width
        svg_height = layout_height
        
        # Create SVG drawing
        dwg = svgwrite.Drawing(output_path, size=(f"{svg_width}px", f"{svg_height}px"))
        
        # Add background
        dwg.add(dwg.rect(insert=(0, 0), size=(svg_width, svg_height), fill='white'))
        
        # Create left layout - Wall Cabinets
        y_offset = margin + self.inches_to_pixels(north_alcove_depth)
        left_group = dwg.g(transform=f"translate({margin},{y_offset})")
        north_w_left, west_h_left, _ = self._render_floor_plan(dwg, left_group, "Wall Cabinets")
        
        # Add wall cabinets to wall cabinets view
        from scripts.engine.cabinet_renderer import CabinetRenderer
        wall_cabinet_renderer = CabinetRenderer(self.measurements, self.scale, self)
        wall_cabinet_renderer.render_wall_cabinets(dwg, left_group, north_w_left, west_h_left)
        
        # Add scale info to left
        scale_text = dwg.text(f'Scale: {self.scale} px/in', 
                             insert=(5, self.inches_to_pixels(west_height) + 40),
                             font_size='10px',
                             font_family='Arial',
                             fill=self.dimension_color)
        left_group.add(scale_text)
        
        dwg.add(left_group)
        
        # Create right layout - Base Cabinets
        right_x_offset = layout_width + gap_between
        right_group = dwg.g(transform=f"translate({right_x_offset},{y_offset})")
        north_w, west_h, _ = self._render_floor_plan(dwg, right_group, "Base Cabinets")
        
        # Add cabinets and appliances to base cabinets view using clean renderer
        from scripts.engine.cabinet_renderer import CabinetRenderer
        cabinet_renderer = CabinetRenderer(self.measurements, self.scale, self)
        cabinet_renderer.render_all(dwg, right_group, north_w, west_h)
        
        # Add scale info to right
        scale_text_right = dwg.text(f'Scale: {self.scale} px/in', 
                                    insert=(5, self.inches_to_pixels(west_height) + 40),
                                    font_size='10px',
                                    font_family='Arial',
                                    fill=self.dimension_color)
        right_group.add(scale_text_right)
        
        dwg.add(right_group)
        
        # Add legend on far right
        legend_x = (layout_width * 2) + gap_between + legend_gap
        legend_y = y_offset
        self._add_legend(dwg, legend_x, legend_y)
        
        # Add shopping list to the right of legend
        shopping_list_x = legend_x + legend_width + shopping_list_gap
        shopping_list_y = y_offset
        self._add_shopping_list(dwg, shopping_list_x, shopping_list_y)
        
        # Save the file
        dwg.save()
        print(f"✅ SVG layout saved to: {output_path}")
        print(f"   Dimensions: {svg_width:.0f}px x {svg_height:.0f}px")
        print(f"   Scale: {self.scale} pixels/inch")
        print(f"   Layout: Side-by-side (Wall Cabinets | Base Cabinets) + Legend")
    
    def _render_floor_plan(self, dwg, parent_group, title_text):
        """
        Helper method to render a single floor plan instance
        Args:
            dwg: SVG drawing object
            parent_group: Parent SVG group to add elements to
            title_text: Title for this layout (e.g., "Wall Cabinets" or "Base Cabinets")
        """
        wall_measurements = self.measurements.get("wall_measurements", {})
        
        # Calculate dimensions
        north_width = wall_measurements["N1"]["measurement_inches"] + wall_measurements["N2"]["measurement_inches"]
        west_height = (wall_measurements["W1"]["measurement_inches"] + 
                      wall_measurements["W2"]["measurement_inches"] + 
                      wall_measurements["W3"]["measurement_inches"])
        
        # Calculate north alcove depth
        north_alcove_depth = 0
        if "segments" in wall_measurements["N2"]:
            import math
            for seg in wall_measurements["N2"]["segments"]:
                direction = seg.get("direction", "E")
                seg_inches = seg["measurement_inches"]
                if direction == "N":
                    north_alcove_depth += seg_inches
                elif direction == "NE":
                    north_alcove_depth += seg_inches * math.sin(math.radians(45))
        
        # Calculate L-shape dimensions
        south_wall_length = (wall_measurements["S1"]["measurement_inches"] + 
                            wall_measurements["S2"]["measurement_inches"] + 
                            wall_measurements["S3"]["measurement_inches"])
        alcove_depth = wall_measurements["E1"]["measurement_inches"]
        
        # Convert to pixels
        main_rect_width = self.inches_to_pixels(north_width)
        main_rect_height = self.inches_to_pixels(west_height)
        south_wall_px = self.inches_to_pixels(south_wall_length)
        alcove_depth_px = self.inches_to_pixels(alcove_depth)
        e2_width_px = self.inches_to_pixels(wall_measurements["E2"]["measurement_inches"])
        e3_height_px = self.inches_to_pixels(wall_measurements["E3"]["measurement_inches"])
        n1_width_px = self.inches_to_pixels(wall_measurements["N1"]["measurement_inches"])
        
        # Add floor background
        floor_group = dwg.g()
        path_points = []
        
        # Build path for floor plan with both alcoves
        path_points.append(f"M 0 0")
        path_points.append(f"L {n1_width_px} 0")
        
        # N2 alcove
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
                    x += seg_length * math.cos(math.radians(-45))
                    y += seg_length * math.sin(math.radians(-45))
                elif direction == "E":
                    x += seg_length
                elif direction == "SE":
                    x += seg_length * math.cos(math.radians(45))
                    y += seg_length * math.sin(math.radians(45))
                elif direction == "S":
                    y += seg_length
                
                path_points.append(f"L {x} {y}")
        else:
            path_points.append(f"L {main_rect_width} 0")
        
        # Rest of room
        path_points.append(f"L {main_rect_width} {e3_height_px}")
        path_points.append(f"L {south_wall_px} {e3_height_px}")
        path_points.append(f"L {south_wall_px} {main_rect_height}")
        path_points.append(f"L 0 {main_rect_height}")
        path_points.append(f"Z")
        
        floor_group.add(dwg.path(
            d=" ".join(path_points),
            fill=self.floor_color,
            stroke='none'
        ))
        parent_group.add(floor_group)
        
        # Draw walls
        walls_group = dwg.g()
        
        # North wall - N1
        y_pos = 0
        x_pos = 0
        n1_total = wall_measurements["N1"]["measurement_inches"]
        
        # Check if N1 has segments (for window)
        if "segments" in wall_measurements["N1"]:
            # Draw N1 segments (includes window)
            start_x = x_pos
            start_y = y_pos
            
            for seg in wall_measurements["N1"]["segments"]:
                seg_width = self.inches_to_pixels(seg["measurement_inches"])
                end_x = start_x + seg_width
                end_y = start_y
                
                if seg["type"] == "wall":
                    walls_group.add(dwg.line(
                        start=(start_x, start_y),
                        end=(end_x, end_y),
                        stroke=self.wall_color,
                        stroke_width=self.wall_width
                    ))
                elif seg["type"] == "window":
                    walls_group.add(dwg.line(
                        start=(start_x, start_y),
                        end=(end_x, end_y),
                        stroke=self.window_color,
                        stroke_width=self.window_width
                    ))
                    # Add window fill/pattern
                    walls_group.add(dwg.rect(
                        insert=(start_x, start_y - 2),
                        size=(seg_width, 4),
                        fill=self.window_color,
                        opacity=0.3
                    ))
                
                start_x = end_x
            
            x_pos += self.inches_to_pixels(n1_total)
        else:
            # Simple wall
            n1_width = self.inches_to_pixels(n1_total)
            walls_group.add(dwg.line(
                start=(x_pos, y_pos),
                end=(x_pos + n1_width, y_pos),
                stroke=self.wall_color,
                stroke_width=self.wall_width
            ))
            x_pos += n1_width
        
        self._add_dimension(dwg, walls_group, 0, y_pos - 20, self.inches_to_pixels(n1_total), y_pos - 20, 
                           f'N1: {n1_total}"')

        
        # N2 - alcove
        n2_total = wall_measurements["N2"]["measurement_inches"]
        
        if "segments" in wall_measurements["N2"]:
            import math
            segments = wall_measurements["N2"]["segments"]
            start_x = x_pos
            start_y = y_pos
            
            for seg in segments:
                seg_length = self.inches_to_pixels(seg["measurement_inches"])
                direction = seg.get("direction", "E")
                seg_inches = seg["measurement_inches"]
                
                # Calculate end point based on direction
                if direction == "N":
                    end_x = start_x
                    end_y = start_y - seg_length
                elif direction == "NE":
                    end_x = start_x + seg_length * math.cos(math.radians(-45))
                    end_y = start_y + seg_length * math.sin(math.radians(-45))
                elif direction == "E":
                    end_x = start_x + seg_length
                    end_y = start_y
                elif direction == "SE":
                    end_x = start_x + seg_length * math.cos(math.radians(45))
                    end_y = start_y + seg_length * math.sin(math.radians(45))
                elif direction == "S":
                    end_x = start_x
                    end_y = start_y + seg_length
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
                
                # Add dimension label for this segment
                mid_x = (start_x + end_x) / 2
                mid_y = (start_y + end_y) / 2
                
                # Offset label based on direction
                if direction == "N":
                    label_x = mid_x - 15
                    label_y = mid_y
                elif direction == "NE":
                    label_x = mid_x - 10
                    label_y = mid_y - 10
                elif direction == "E":
                    label_x = mid_x
                    label_y = mid_y - 10
                elif direction == "SE":
                    label_x = mid_x + 10
                    label_y = mid_y - 10
                else:
                    label_x = mid_x
                    label_y = mid_y - 10
                
                walls_group.add(dwg.text(
                    f'{seg_inches}"',
                    insert=(label_x, label_y),
                    font_size='10px',
                    font_family='Arial',
                    fill=self.dimension_color,
                    text_anchor='middle'
                ))
                
                start_x = end_x
                start_y = end_y
            
            x_pos += self.inches_to_pixels(n2_total)
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
        
        # East wall - E3
        east_x = x_pos
        e3_height = self.inches_to_pixels(wall_measurements["E3"]["measurement_inches"])
        walls_group.add(dwg.line(
            start=(east_x, y_pos),
            end=(east_x, e3_height),
            stroke=self.wall_color,
            stroke_width=self.wall_width
        ))
        self._add_dimension(dwg, walls_group, east_x + 20, y_pos, east_x + 20, e3_height,
                           f'E3: {wall_measurements["E3"]["measurement_inches"]}"', vertical=True)
        
        # E2 - with possible door
        e2_total = wall_measurements["E2"]["measurement_inches"]
        south_wall_end_x = self.inches_to_pixels(south_wall_length)
        
        if "segments" in wall_measurements["E2"]:
            # Draw E2 segments (includes door)
            start_x = east_x
            start_y = e3_height
            
            for seg in wall_measurements["E2"]["segments"]:
                seg_width = self.inches_to_pixels(seg["measurement_inches"])
                end_x = start_x - seg_width
                end_y = start_y
                
                if seg["type"] == "wall":
                    walls_group.add(dwg.line(
                        start=(start_x, start_y),
                        end=(end_x, end_y),
                        stroke=self.wall_color,
                        stroke_width=self.wall_width
                    ))
                elif seg["type"] == "door":
                    walls_group.add(dwg.line(
                        start=(start_x, start_y),
                        end=(end_x, end_y),
                        stroke=self.door_color,
                        stroke_width=self.door_width
                    ))
                    # Door arc
                    radius = seg_width
                    walls_group.add(dwg.path(
                        d=f"M {start_x} {start_y} A {radius} {radius} 0 0 0 {end_x} {end_y - radius}",
                        fill='none',
                        stroke=self.door_color,
                        stroke_width=1,
                        stroke_dasharray='3,3'
                    ))
                
                start_x = end_x
        else:
            # Simple wall
            walls_group.add(dwg.line(
                start=(east_x, e3_height),
                end=(south_wall_end_x, e3_height),
                stroke=self.wall_color,
                stroke_width=self.wall_width
            ))
        
        self._add_dimension(dwg, walls_group, south_wall_end_x, e3_height - 20, east_x, e3_height - 20,
                           f'E2: {e2_total}"')
        
        # E1 - check if door or wall
        e1_height = self.inches_to_pixels(wall_measurements["E1"]["measurement_inches"])
        e1_type = wall_measurements["E1"].get("type", "wall")
        
        if e1_type == "door":
            # Draw door with arc swinging westward into kitchen (hinge on south side)
            walls_group.add(dwg.line(
                start=(south_wall_end_x, e3_height),
                end=(south_wall_end_x, e3_height + e1_height),
                stroke=self.door_color,
                stroke_width=self.door_width
            ))
            # Door arc - hinge on south, swing westward from north end
            radius = e1_height
            walls_group.add(dwg.path(
                d=f"M {south_wall_end_x} {e3_height} A {radius} {radius} 0 0 0 {south_wall_end_x - radius} {e3_height + e1_height}",
                fill='none',
                stroke=self.door_color,
                stroke_width=1,
                stroke_dasharray='2,2'
            ))
        else:
            walls_group.add(dwg.line(
                start=(south_wall_end_x, e3_height),
                end=(south_wall_end_x, e3_height + e1_height),
                stroke=self.wall_color,
                stroke_width=self.wall_width
            ))
        self._add_dimension(dwg, walls_group, south_wall_end_x + 20, e3_height, south_wall_end_x + 20, e3_height + e1_height,
                           f'E1: {wall_measurements["E1"]["measurement_inches"]}"', vertical=True)
        
        # South wall
        y_pos = self.inches_to_pixels(west_height)
        x_pos = 0
        
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
        
        # S2 - check if entryway or door
        s2_width = self.inches_to_pixels(wall_measurements["S2"]["measurement_inches"])
        s2_type = wall_measurements["S2"].get("type", "door")
        
        if s2_type == "entryway":
            # Draw as dashed line for entryway
            walls_group.add(dwg.line(
                start=(x_pos, y_pos),
                end=(x_pos + s2_width, y_pos),
                stroke='#999999',
                stroke_width=1,
                stroke_dasharray='5,5'
            ))
            self._add_dimension(dwg, walls_group, x_pos, y_pos + 20, x_pos + s2_width, y_pos + 20,
                               f'S2: {wall_measurements["S2"]["measurement_inches"]}" (entryway)')
        else:
            # Draw as door with arc
            walls_group.add(dwg.line(
                start=(x_pos, y_pos),
                end=(x_pos + s2_width, y_pos),
                stroke=self.door_color,
                stroke_width=self.door_width
            ))
            radius = s2_width
            walls_group.add(dwg.path(
                d=f"M {x_pos} {y_pos} A {radius} {radius} 0 0 1 {x_pos + radius} {y_pos - radius}",
                fill='none',
                stroke=self.door_color,
                stroke_width=1,
                stroke_dasharray='3,3'
            ))
            self._add_dimension(dwg, walls_group, x_pos, y_pos + 20, x_pos + s2_width, y_pos + 20,
                               f'S2: {wall_measurements["S2"]["measurement_inches"]}" (door)')
        x_pos += s2_width
        
        # S3
        s3_width = self.inches_to_pixels(wall_measurements["S3"]["measurement_inches"])
        walls_group.add(dwg.line(
            start=(x_pos, y_pos),
            end=(x_pos + s3_width, y_pos),
            stroke=self.wall_color,
            stroke_width=self.wall_width
        ))
        self._add_dimension(dwg, walls_group, x_pos, y_pos + 20, x_pos + s3_width, y_pos + 20,
                           f'S3: {wall_measurements["S3"]["measurement_inches"]}"')
        
        # West wall
        x_pos = 0
        y_pos = 0
        
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
        
        # W2 - check if entryway or door
        w2_height = self.inches_to_pixels(wall_measurements["W2"]["measurement_inches"])
        w2_type = wall_measurements["W2"].get("type", "door")
        
        if w2_type == "entryway":
            # Draw as dashed line for entryway
            walls_group.add(dwg.line(
                start=(x_pos, y_pos),
                end=(x_pos, y_pos + w2_height),
                stroke='#999999',
                stroke_width=1,
                stroke_dasharray='5,5'
            ))
            self._add_dimension(dwg, walls_group, x_pos - 20, y_pos, x_pos - 20, y_pos + w2_height,
                               f'W2: {wall_measurements["W2"]["measurement_inches"]}" (entryway)', vertical=True)
        else:
            # Draw as door with arc
            walls_group.add(dwg.line(
                start=(x_pos, y_pos),
                end=(x_pos, y_pos + w2_height),
                stroke=self.door_color,
                stroke_width=self.door_width
            ))
            radius = w2_height
            walls_group.add(dwg.path(
                d=f"M {x_pos} {y_pos} A {radius} {radius} 0 0 1 {x_pos + radius} {y_pos + radius}",
                fill='none',
                stroke=self.door_color,
                stroke_width=1,
                stroke_dasharray='3,3'
            ))
            self._add_dimension(dwg, walls_group, x_pos - 20, y_pos, x_pos - 20, y_pos + w2_height,
                               f'W2: {wall_measurements["W2"]["measurement_inches"]}" (door)', vertical=True)
        y_pos += w2_height
        
        # W3
        w3_height = self.inches_to_pixels(wall_measurements["W3"]["measurement_inches"])
        walls_group.add(dwg.line(
            start=(x_pos, y_pos),
            end=(x_pos, y_pos + w3_height),
            stroke=self.wall_color,
            stroke_width=self.wall_width
        ))
        self._add_dimension(dwg, walls_group, x_pos - 20, y_pos, x_pos - 20, y_pos + w3_height,
                           f'W3: {wall_measurements["W3"]["measurement_inches"]}"', vertical=True)
        
        parent_group.add(walls_group)
        
        # Add title
        title_y = -self.inches_to_pixels(north_alcove_depth) - 20
        title = dwg.text(title_text, 
                        insert=(self.inches_to_pixels(north_width) / 2, title_y),
                        text_anchor='middle',
                        font_size='18px',
                        font_family='Arial',
                        fill=self.text_color,
                        font_weight='bold')
        parent_group.add(title)
        
        # Add compass
        self._add_compass(dwg, parent_group, self.inches_to_pixels(north_width) - 50, 50)
        
        return north_width, west_height, north_alcove_depth
    
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
    
    def _render_wall_segment(self, dwg, walls_group, start_x, start_y, end_x, end_y, wall_type="wall", orientation='horizontal'):
        """Render a single wall segment with door arc if needed
        
        Args:
            wall_type: 'wall', 'door', 'entryway', or 'window'
            orientation: 'horizontal' or 'vertical' - determines door arc direction
        """
        if wall_type == "entryway":
            walls_group.add(dwg.line(
                start=(start_x, start_y),
                end=(end_x, end_y),
                stroke='#999999',
                stroke_width=1,
                stroke_dasharray='5,5'
            ))
        elif wall_type == "window":
            walls_group.add(dwg.line(
                start=(start_x, start_y),
                end=(end_x, end_y),
                stroke=self.window_color,
                stroke_width=self.window_width
            ))
            # Window fill
            if orientation == 'horizontal':
                walls_group.add(dwg.rect(
                    insert=(start_x, start_y - 2),
                    size=(abs(end_x - start_x), 4),
                    fill=self.window_color,
                    opacity=0.3
                ))
            else:
                walls_group.add(dwg.rect(
                    insert=(start_x - 2, start_y),
                    size=(4, abs(end_y - start_y)),
                    fill=self.window_color,
                    opacity=0.3
                ))
        elif wall_type == "door":
            walls_group.add(dwg.line(
                start=(start_x, start_y),
                end=(end_x, end_y),
                stroke=self.door_color,
                stroke_width=self.door_width
            ))
            # Add door arc based on orientation
            if orientation == 'horizontal':
                length = abs(end_x - start_x)
                if end_x > start_x:  # Opening to the right
                    walls_group.add(dwg.path(
                        d=f"M {start_x} {start_y} A {length} {length} 0 0 1 {end_x} {start_y - length}",
                        fill='none',
                        stroke=self.door_color,
                        stroke_width=1,
                        stroke_dasharray='2,2'
                    ))
                else:  # Opening to the left
                    walls_group.add(dwg.path(
                        d=f"M {start_x} {start_y} A {length} {length} 0 0 0 {end_x} {end_y - length}",
                        fill='none',
                        stroke=self.door_color,
                        stroke_width=1,
                        stroke_dasharray='2,2'
                    ))
            else:  # vertical
                length = abs(end_y - start_y)
                if end_y > start_y:  # Opening downward (swing westward into kitchen)
                    walls_group.add(dwg.path(
                        d=f"M {start_x} {start_y} A {length} {length} 0 0 0 {start_x - length} {end_y}",
                        fill='none',
                        stroke=self.door_color,
                        stroke_width=1,
                        stroke_dasharray='2,2'
                    ))
                else:  # Opening upward
                    walls_group.add(dwg.path(
                        d=f"M {start_x} {start_y} A {length} {length} 0 0 1 {start_x - length} {end_y}",
                        fill='none',
                        stroke=self.door_color,
                        stroke_width=1,
                        stroke_dasharray='2,2'
                    ))
        else:  # Regular wall
            walls_group.add(dwg.line(
                start=(start_x, start_y),
                end=(end_x, end_y),
                stroke=self.wall_color,
                stroke_width=self.wall_width
            ))
    
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
    
    def _add_legend(self, dwg, x, y):
        """Add legend showing line types and symbols"""
        legend_group = dwg.g()
        
        # Legend title
        legend_group.add(dwg.text('Legend',
                                  insert=(x, y - 10),
                                  font_size='14px',
                                  font_family='Arial',
                                  fill=self.text_color,
                                  font_weight='bold'))
        
        # Legend box background
        legend_group.add(dwg.rect(
            insert=(x - 5, y),
            size=(145, 180),
            fill='#f9f9f9',
            stroke='#cccccc',
            stroke_width=1
        ))
        
        line_y = y + 20
        line_length = 30
        spacing = 30
        
        # Wall
        legend_group.add(dwg.line(
            start=(x + 5, line_y),
            end=(x + 5 + line_length, line_y),
            stroke=self.wall_color,
            stroke_width=self.wall_width
        ))
        legend_group.add(dwg.text('Wall',
                                  insert=(x + 5 + line_length + 10, line_y + 5),
                                  font_size='11px',
                                  font_family='Arial',
                                  fill=self.text_color))
        
        # Door
        line_y += spacing
        legend_group.add(dwg.line(
            start=(x + 5, line_y),
            end=(x + 5 + line_length, line_y),
            stroke=self.door_color,
            stroke_width=self.door_width
        ))
        # Door arc
        legend_group.add(dwg.path(
            d=f"M {x + 5} {line_y} A 15 15 0 0 1 {x + 5 + 15} {line_y - 15}",
            fill='none',
            stroke=self.door_color,
            stroke_width=1,
            stroke_dasharray='2,2'
        ))
        legend_group.add(dwg.text('Door',
                                  insert=(x + 5 + line_length + 10, line_y + 5),
                                  font_size='11px',
                                  font_family='Arial',
                                  fill=self.text_color))
        
        # Window
        line_y += spacing
        legend_group.add(dwg.line(
            start=(x + 5, line_y),
            end=(x + 5 + line_length, line_y),
            stroke=self.window_color,
            stroke_width=self.window_width
        ))
        legend_group.add(dwg.rect(
            insert=(x + 5, line_y - 2),
            size=(line_length, 4),
            fill=self.window_color,
            opacity=0.3
        ))
        legend_group.add(dwg.text('Window',
                                  insert=(x + 5 + line_length + 10, line_y + 5),
                                  font_size='11px',
                                  font_family='Arial',
                                  fill=self.text_color))
        
        # Dimension line
        line_y += spacing
        legend_group.add(dwg.line(
            start=(x + 5, line_y),
            end=(x + 5 + line_length, line_y),
            stroke=self.dimension_color,
            stroke_width=0.5
        ))
        legend_group.add(dwg.line(
            start=(x + 5, line_y - 3),
            end=(x + 5, line_y + 3),
            stroke=self.dimension_color,
            stroke_width=0.5
        ))
        legend_group.add(dwg.line(
            start=(x + 5 + line_length, line_y - 3),
            end=(x + 5 + line_length, line_y + 3),
            stroke=self.dimension_color,
            stroke_width=0.5
        ))
        legend_group.add(dwg.text('Dimension',
                                  insert=(x + 5 + line_length + 10, line_y + 5),
                                  font_size='11px',
                                  font_family='Arial',
                                  fill=self.text_color))
        
        # Floor
        line_y += spacing
        legend_group.add(dwg.rect(
            insert=(x + 5, line_y - 8),
            size=(line_length, 16),
            fill=self.floor_color,
            stroke='none'
        ))
        legend_group.add(dwg.text('Floor',
                                  insert=(x + 5 + line_length + 10, line_y + 5),
                                  font_size='11px',
                                  font_family='Arial',
                                  fill=self.text_color))
        
        # Alcove note
        line_y += spacing + 5
        legend_group.add(dwg.text('Alcove:',
                                  insert=(x + 5, line_y),
                                  font_size='10px',
                                  font_family='Arial',
                                  fill=self.text_color,
                                  font_weight='bold'))
        line_y += 15
        legend_group.add(dwg.text('N2 (north)',
                                  insert=(x + 10, line_y),
                                  font_size='9px',
                                  font_family='Arial',
                                  fill=self.text_color))
        line_y += 12
        legend_group.add(dwg.text('E1-E2 (SE)',
                                  insert=(x + 10, line_y),
                                  font_size='9px',
                                  font_family='Arial',
                                  fill=self.text_color))
        
        dwg.add(legend_group)
    
    def _add_shopping_list(self, dwg, x, y):
        """Add shopping list for cabinets and items to buy"""
        shopping_group = dwg.g()
        
        # Title
        shopping_group.add(dwg.text('Shopping List',
                                    insert=(x, y - 10),
                                    font_size='14px',
                                    font_family='Arial',
                                    fill=self.text_color,
                                    font_weight='bold'))
        
        # Get shopping list from config
        shopping_items = self.measurements.get("shopping_list", {})
        
        # Calculate box height based on items
        base_height = 60
        item_height = 0
        
        # Count items
        wall_cabinets = shopping_items.get("wall_cabinets", [])
        base_cabinets = shopping_items.get("base_cabinets", [])
        appliances = shopping_items.get("appliances", [])
        other = shopping_items.get("other", [])
        
        total_items = len(wall_cabinets) + len(base_cabinets) + len(appliances) + len(other)
        if total_items > 0:
            item_height = total_items * 18 + 80  # Each item ~18px, sections add space
        else:
            item_height = 40  # Placeholder text
        
        box_height = max(base_height + item_height, 180)
        
        # Shopping list box background
        shopping_group.add(dwg.rect(
            insert=(x - 5, y),
            size=(195, box_height),
            fill='#f9f9f9',
            stroke='#cccccc',
            stroke_width=1
        ))
        
        line_y = y + 20
        
        if total_items == 0:
            # Placeholder text
            shopping_group.add(dwg.text('No items yet.',
                                        insert=(x + 5, line_y),
                                        font_size='10px',
                                        font_family='Arial',
                                        fill='#999999',
                                        font_style='italic'))
            line_y += 20
            shopping_group.add(dwg.text('Add cabinets to',
                                        insert=(x + 5, line_y),
                                        font_size='10px',
                                        font_family='Arial',
                                        fill='#999999',
                                        font_style='italic'))
            line_y += 15
            shopping_group.add(dwg.text('generate list.',
                                        insert=(x + 5, line_y),
                                        font_size='10px',
                                        font_family='Arial',
                                        fill='#999999',
                                        font_style='italic'))
        else:
            # Wall Cabinets
            if wall_cabinets:
                shopping_group.add(dwg.text('Wall Cabinets:',
                                            insert=(x + 5, line_y),
                                            font_size='11px',
                                            font_family='Arial',
                                            fill=self.text_color,
                                            font_weight='bold'))
                line_y += 15
                for item in wall_cabinets:
                    qty = item.get("quantity", 1)
                    width = item.get("width_inches", "?")
                    height = item.get("height_inches", "?")
                    shopping_group.add(dwg.text(f'• {qty}x {width}"W x {height}"H',
                                                insert=(x + 10, line_y),
                                                font_size='10px',
                                                font_family='Arial',
                                                fill=self.text_color))
                    line_y += 15
                line_y += 5
            
            # Base Cabinets
            if base_cabinets:
                shopping_group.add(dwg.text('Base Cabinets:',
                                            insert=(x + 5, line_y),
                                            font_size='11px',
                                            font_family='Arial',
                                            fill=self.text_color,
                                            font_weight='bold'))
                line_y += 15
                for item in base_cabinets:
                    qty = item.get("quantity", 1)
                    width = item.get("width_inches", "?")
                    shopping_group.add(dwg.text(f'• {qty}x {width}"W',
                                                insert=(x + 10, line_y),
                                                font_size='10px',
                                                font_family='Arial',
                                                fill=self.text_color))
                    line_y += 15
                line_y += 5
            
            # Appliances
            if appliances:
                shopping_group.add(dwg.text('Appliances:',
                                            insert=(x + 5, line_y),
                                            font_size='11px',
                                            font_family='Arial',
                                            fill=self.text_color,
                                            font_weight='bold'))
                line_y += 15
                for item in appliances:
                    qty = item.get("quantity", 1)
                    name = item.get("name", "Item")
                    shopping_group.add(dwg.text(f'• {qty}x {name}',
                                                insert=(x + 10, line_y),
                                                font_size='10px',
                                                font_family='Arial',
                                                fill=self.text_color))
                    line_y += 15
                line_y += 5
            
            # Other items
            if other:
                shopping_group.add(dwg.text('Other:',
                                            insert=(x + 5, line_y),
                                            font_size='11px',
                                            font_family='Arial',
                                            fill=self.text_color,
                                            font_weight='bold'))
                line_y += 15
                for item in other:
                    qty = item.get("quantity", 1)
                    name = item.get("name", "Item")
                    shopping_group.add(dwg.text(f'• {qty}x {name}',
                                                insert=(x + 10, line_y),
                                                font_size='10px',
                                                font_family='Arial',
                                                fill=self.text_color))
                    line_y += 15
        
        dwg.add(shopping_group)


if __name__ == "__main__":
    renderer = SVGRenderer(scale=3.0)
    renderer.create_kitchen_layout()
