"""
Clean, simple cabinet rendering with automatic overlap prevention
"""

class Rectangle:
    """Simple rectangle in inches"""
    def __init__(self, x, y, width, height, label=""):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.label = label
    
    def overlaps(self, other):
        """Check if this rectangle overlaps with another"""
        return not (self.x + self.width <= other.x or  # self is left of other
                   other.x + other.width <= self.x or   # other is left of self
                   self.y + self.height <= other.y or   # self is above other
                   other.y + other.height <= self.y)    # other is above self


class CabinetRenderer:
    """Handles rendering cabinets and appliances with overlap prevention"""
    
    def __init__(self, measurements, scale, svg_renderer):
        self.measurements = measurements
        self.scale = scale
        self.svg_renderer = svg_renderer
        self.placed_items = []  # Track all placed rectangles
        
    def inches_to_pixels(self, inches):
        return inches * self.scale
    
    def can_place(self, rect):
        """Check if rectangle can be placed without overlapping"""
        for existing in self.placed_items:
            if rect.overlaps(existing):
                return False
        return True
    
    def place_item(self, rect):
        """Mark rectangle as placed"""
        self.placed_items.append(rect)
    
    def render_all(self, dwg, group, north_width, west_height):
        """Render all cabinets and appliances"""
        appliances = self.measurements.get("appliances", {})
        base_cabinets = self.measurements.get("base_cabinets", {})
        
        # Constants
        CABINET_DEPTH = 24
        
        # Render appliances first (highest priority)
        self._render_appliances(dwg, group, appliances, north_width, west_height)
        
        # Render corner cabinet (second priority, marks corner space)
        self._render_corner_cabinet(dwg, group, appliances, north_width, west_height, CABINET_DEPTH)
        
        # Render base cabinets (check for overlaps)
        self._render_base_cabinets(dwg, group, base_cabinets, north_width, west_height, CABINET_DEPTH)
    
    def _render_appliances(self, dwg, group, appliances, north_width, west_height):
        """Render all appliances"""
        # Fridge on E3
        if "fridge" in appliances:
            fridge = appliances["fridge"]
            if fridge["location"] == "E3":
                x = north_width - fridge["depth_inches"]
                y = fridge["position_from_start_inches"]
                w = fridge["depth_inches"]
                h = fridge["width_inches"]
                
                rect = Rectangle(x, y, w, h, "FRIDGE")
                self.place_item(rect)
                
                px = self.inches_to_pixels(x)
                py = self.inches_to_pixels(y)
                pw = self.inches_to_pixels(w)
                ph = self.inches_to_pixels(h)
                
                group.add(dwg.rect(insert=(px, py), size=(pw, ph),
                                  fill='#C0C0C0', stroke='#000', stroke_width=1))
                group.add(dwg.text('FRIDGE', insert=(px + pw/2, py + ph/2),
                                  text_anchor='middle', font_size='10px', fill='#000'))
        
        # Range on E3
        if "range" in appliances:
            range_appl = appliances["range"]
            if range_appl["location"] == "E3":
                x = north_width - range_appl["depth_inches"]
                y = range_appl["position_from_start_inches"]
                w = range_appl["depth_inches"]
                h = range_appl["width_inches"]
                
                rect = Rectangle(x, y, w, h, "RANGE")
                self.place_item(rect)
                
                px = self.inches_to_pixels(x)
                py = self.inches_to_pixels(y)
                pw = self.inches_to_pixels(w)
                ph = self.inches_to_pixels(h)
                
                group.add(dwg.rect(insert=(px, py), size=(pw, ph),
                                  fill='#404040', stroke='#000', stroke_width=1))
                group.add(dwg.text('RANGE', insert=(px + pw/2, py + ph/2),
                                  text_anchor='middle', font_size='9px', fill='#FFF'))
                
                # Draw burners
                burner_size = 6
                for i in range(2):
                    for j in range(2):
                        bx = px + pw/3 * (i + 1)
                        by = py + ph/3 * (j + 1)
                        group.add(dwg.circle(center=(bx, by), r=burner_size/2,
                                            fill='#666', stroke='#000', stroke_width=0.5))
        
        # Sink on N1
        if "sink" in appliances:
            sink = appliances["sink"]
            if sink["location"] == "N1":
                x = sink["position_from_start_inches"]
                y = 0
                w = sink["width_inches"]
                h = sink["depth_inches"]
                
                rect = Rectangle(x, y, w, h, "SINK")
                self.place_item(rect)
                
                px = self.inches_to_pixels(x)
                py = 0
                pw = self.inches_to_pixels(w)
                ph = self.inches_to_pixels(h)
                
                group.add(dwg.rect(insert=(px, py), size=(pw, ph),
                                  fill='#87CEEB', stroke='#000', stroke_width=1))
                group.add(dwg.ellipse(center=(px + pw/2, ph/2), r=(pw*0.4, ph*0.3),
                                     fill='#4682B4', stroke='#000', stroke_width=1))
        
        # Dishwasher on N1
        if "dishwasher" in appliances:
            dw = appliances["dishwasher"]
            if dw["location"] == "N1":
                x = dw["position_from_start_inches"]
                y = 0
                w = dw["width_inches"]
                h = dw["depth_inches"]
                
                rect = Rectangle(x, y, w, h, "DW")
                self.place_item(rect)
                
                px = self.inches_to_pixels(x)
                py = 0
                pw = self.inches_to_pixels(w)
                ph = self.inches_to_pixels(h)
                
                group.add(dwg.rect(insert=(px, py), size=(pw, ph),
                                  fill='#708090', stroke='#000', stroke_width=1))
                group.add(dwg.text('DW', insert=(px + pw/2, ph/2),
                                  text_anchor='middle', font_size='10px', fill='#FFF'))
    
    def _render_corner_cabinet(self, dwg, group, appliances, north_width, west_height, CABINET_DEPTH):
        """Render floor-to-ceiling corner cabinet at SW corner"""
        if "corner_cabinet" not in appliances:
            return
        
        cc = appliances["corner_cabinet"]
        if cc["location"] == "SW_CORNER":
            # Corner cabinet is 36"x36" occupying the SW corner
            cc_size = cc["width_inches"]  # 36"
            
            # The corner cabinet is a full 36"x36" square in the corner
            # It occupies 36" along S1 (east-west) and 36" along W3 (north-south)
            
            # Mark S1 space as occupied - 36" along S1 wall, 36" deep (not CABINET_DEPTH)
            rect_s1 = Rectangle(0, west_height - cc_size, cc_size, cc_size, "CC-S1")
            self.place_item(rect_s1)
            
            # Draw visual corner piece as full 36x36 square
            px = 0
            py = self.inches_to_pixels(west_height - cc_size)
            pw = self.inches_to_pixels(cc_size)
            ph = self.inches_to_pixels(cc_size)
            
            group.add(dwg.rect(insert=(px, py), size=(pw, ph),
                              fill='#A0522D', stroke='#000', stroke_width=2))
            group.add(dwg.text('CORNER', insert=(px + pw/2, py + ph/2 - 5),
                              text_anchor='middle', font_size='8px', font_weight='bold', fill='#FFF'))
            group.add(dwg.text('CABINET', insert=(px + pw/2, py + ph/2 + 5),
                              text_anchor='middle', font_size='8px', font_weight='bold', fill='#FFF'))
    
    def _render_base_cabinets(self, dwg, group, base_cabinets, north_width, west_height, CABINET_DEPTH):
        """Render all base cabinets, skipping overlaps"""
        
        # N1 cabinets
        if "N1" in base_cabinets:
            for i, cab in enumerate(base_cabinets["N1"]):
                if cab.get("type") in ["sink_base", "dishwasher_space", "fridge_space"]:
                    continue
                
                x = cab["position_from_start"]
                y = 0
                w = cab["width_inches"]
                h = CABINET_DEPTH
                
                rect = Rectangle(x, y, w, h, f"N1-{i+1}")
                if self.can_place(rect):
                    self.place_item(rect)
                    self._draw_cabinet(dwg, group, rect, '#D2691E')
        
        # E3 cabinets
        if "E3" in base_cabinets:
            for i, cab in enumerate(base_cabinets["E3"]):
                if cab.get("type") in ["lazy_susan", "fridge_space", "range_space"]:
                    continue
                
                x = north_width - CABINET_DEPTH
                y = cab["position_from_start"]
                w = CABINET_DEPTH
                h = cab["width_inches"]
                
                rect = Rectangle(x, y, w, h, f"E3-{i+1}")
                if self.can_place(rect):
                    self.place_item(rect)
                    self._draw_cabinet(dwg, group, rect, '#D2691E')
        
        # S1 cabinets
        if "S1" in base_cabinets:
            for i, cab in enumerate(base_cabinets["S1"]):
                if cab.get("type") in ["lazy_susan", "sink_base", "dishwasher_space"]:
                    continue
                
                x = cab["position_from_start"]
                y = west_height - CABINET_DEPTH
                w = cab["width_inches"]
                h = CABINET_DEPTH
                
                rect = Rectangle(x, y, w, h, f"S1-{i+1}")
                if self.can_place(rect):
                    self.place_item(rect)
                    self._draw_cabinet(dwg, group, rect, '#D2691E')
        
        # W3 cabinets
        if "W3" in base_cabinets:
            w1_h = self.measurements["wall_measurements"]["W1"]["measurement_inches"]
            w2_h = self.measurements["wall_measurements"]["W2"]["measurement_inches"]
            w3_start = w1_h + w2_h
            
            for i, cab in enumerate(base_cabinets["W3"]):
                if cab.get("type") in ["lazy_susan"]:
                    continue
                
                x = 0
                y = w3_start + cab["position_from_start"]
                w = CABINET_DEPTH
                h = cab["width_inches"]
                
                rect = Rectangle(x, y, w, h, f"W3-{i+1}")
                if self.can_place(rect):
                    self.place_item(rect)
                    self._draw_cabinet(dwg, group, rect, '#D2691E')

    
    def _draw_cabinet(self, dwg, group, rect, color):
        """Draw a single cabinet with label"""
        px = self.inches_to_pixels(rect.x)
        py = self.inches_to_pixels(rect.y)
        pw = self.inches_to_pixels(rect.width)
        ph = self.inches_to_pixels(rect.height)
        
        group.add(dwg.rect(insert=(px, py), size=(pw, ph),
                          fill=color, stroke='#000', stroke_width=1, opacity=0.7))
        
        # Label
        group.add(dwg.text(rect.label, insert=(px + pw/2, py + ph/2 - 5),
                          text_anchor='middle', font_size='9px', font_weight='bold', fill='#000'))
        group.add(dwg.text(f'{int(rect.width)}"W', insert=(px + pw/2, py + ph/2 + 5),
                          text_anchor='middle', font_size='8px', fill='#000'))
    
    def render_wall_cabinets(self, dwg, group, north_width, west_height):
        """Render all wall cabinets including corner cabinet"""
        wall_cabinets = self.measurements.get("wall_cabinets", {})
        appliances = self.measurements.get("appliances", {})
        CABINET_DEPTH = 12  # Wall cabinets are 12" deep
        
        # First, render corner cabinet if it exists (occupies full 36x36 corner)
        if "corner_cabinet" in appliances:
            cc = appliances["corner_cabinet"]
            if cc["location"] == "SW_CORNER":
                # Corner cabinet extends 36" along both walls at full 36" depth
                cc_size = cc["width_inches"]  # 36"
                
                # Draw corner cabinet on wall view as 36x36 to match base view
                px = 0
                py = self.inches_to_pixels(west_height - cc_size)
                pw = self.inches_to_pixels(cc_size)
                ph = self.inches_to_pixels(cc_size)  # Full 36" depth, not just 12"
                
                group.add(dwg.rect(insert=(px, py), size=(pw, ph),
                                  fill='#A0522D', stroke='#000', stroke_width=2))
                group.add(dwg.text('CORNER', insert=(px + pw/2, py + ph/2 - 5),
                                  text_anchor='middle', font_size='8px', font_weight='bold', fill='#FFF'))
                group.add(dwg.text('CABINET', insert=(px + pw/2, py + ph/2 + 5),
                                  text_anchor='middle', font_size='8px', font_weight='bold', fill='#FFF'))
        
        # N1 wall cabinets
        if "N1" in wall_cabinets:
            for i, cab in enumerate(wall_cabinets["N1"]):
                x = cab["position_from_start"]
                y = 0
                w = cab["width_inches"]
                h = CABINET_DEPTH
                
                rect = Rectangle(x, y, w, h, f'N1-{i+1}: {w}"W, {cab["height_inches"]}"H')
                px = self.inches_to_pixels(x)
                py = 0
                pw = self.inches_to_pixels(w)
                ph = self.inches_to_pixels(h)
                
                group.add(dwg.rect(insert=(px, py), size=(pw, ph),
                                  fill='#CD853F', stroke='#000', stroke_width=1, opacity=0.8))
                group.add(dwg.text(f'N1-{i+1}: {w}"W', insert=(px + pw/2, py + ph/2 - 3),
                                  text_anchor='middle', font_size='8px', font_weight='bold', fill='#000'))
                group.add(dwg.text(f'{cab["height_inches"]}"H', insert=(px + pw/2, py + ph/2 + 6),
                                  text_anchor='middle', font_size='8px', fill='#000'))
        
        # E3 wall cabinets
        if "E3" in wall_cabinets:
            for i, cab in enumerate(wall_cabinets["E3"]):
                x = north_width - CABINET_DEPTH
                y = cab["position_from_start"]
                w = CABINET_DEPTH
                h = cab["width_inches"]
                
                px = self.inches_to_pixels(x)
                py = self.inches_to_pixels(y)
                pw = self.inches_to_pixels(w)
                ph = self.inches_to_pixels(h)
                
                group.add(dwg.rect(insert=(px, py), size=(pw, ph),
                                  fill='#CD853F', stroke='#000', stroke_width=1, opacity=0.8))
                group.add(dwg.text(f'E3-{i+1}', insert=(px + pw/2, py + ph/2 - 5),
                                  text_anchor='middle', font_size='8px', font_weight='bold', fill='#000'))
                group.add(dwg.text(f'{cab["width_inches"]}"W', insert=(px + pw/2, py + ph/2 + 3),
                                  text_anchor='middle', font_size='7px', fill='#000'))
                group.add(dwg.text(f'{cab["height_inches"]}"H', insert=(px + pw/2, py + ph/2 + 10),
                                  text_anchor='middle', font_size='7px', fill='#000'))
        
        # S1 wall cabinets
        if "S1" in wall_cabinets:
            for i, cab in enumerate(wall_cabinets["S1"]):
                x = cab["position_from_start"]
                y = west_height - CABINET_DEPTH
                w = cab["width_inches"]
                h = CABINET_DEPTH
                
                px = self.inches_to_pixels(x)
                py = self.inches_to_pixels(y)
                pw = self.inches_to_pixels(w)
                ph = self.inches_to_pixels(h)
                
                group.add(dwg.rect(insert=(px, py), size=(pw, ph),
                                  fill='#CD853F', stroke='#000', stroke_width=1, opacity=0.8))
                group.add(dwg.text(f'S1-{i+1}: {w}"W', insert=(px + pw/2, py + ph/2 - 3),
                                  text_anchor='middle', font_size='8px', font_weight='bold', fill='#000'))
                group.add(dwg.text(f'{cab["height_inches"]}"H', insert=(px + pw/2, py + ph/2 + 6),
                                  text_anchor='middle', font_size='8px', fill='#000'))
        
        # W3 wall cabinets
        if "W3" in wall_cabinets:
            w1_h = self.measurements["wall_measurements"]["W1"]["measurement_inches"]
            w2_h = self.measurements["wall_measurements"]["W2"]["measurement_inches"]
            w3_start = w1_h + w2_h
            
            for i, cab in enumerate(wall_cabinets["W3"]):
                x = 0
                y = w3_start + cab["position_from_start"]
                w = CABINET_DEPTH
                h = cab["width_inches"]
                
                px = 0
                py = self.inches_to_pixels(y)
                pw = self.inches_to_pixels(w)
                ph = self.inches_to_pixels(h)
                
                group.add(dwg.rect(insert=(px, py), size=(pw, ph),
                                  fill='#CD853F', stroke='#000', stroke_width=1, opacity=0.8))
                group.add(dwg.text(f'W3-{i+1}', insert=(px + pw/2, py + ph/2 - 5),
                                  text_anchor='middle', font_size='8px', font_weight='bold', fill='#000'))
                group.add(dwg.text(f'{h}"W', insert=(px + pw/2, py + ph/2 + 3),
                                  text_anchor='middle', font_size='7px', fill='#000'))
                group.add(dwg.text(f'{cab["height_inches"]}"H', insert=(px + pw/2, py + ph/2 + 10),
                                  text_anchor='middle', font_size='7px', fill='#000'))
