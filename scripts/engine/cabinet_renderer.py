"""
Clean, optimized cabinet rendering with automatic overlap prevention
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
        return not (self.x + self.width <= other.x or
                   other.x + other.width <= self.x or
                   self.y + self.height <= other.y or
                   other.y + other.height <= self.y)


class CabinetRenderer:
    """Handles rendering cabinets and appliances with overlap prevention"""
    
    # Constants
    CABINET_DEPTH = 24
    CABINET_COLORS = {
        'base': '#D2691E',
        'wall': '#CD853F',
        'lazy_susan': '#A0522D',
        'tall': '#8B4513',
        'fridge': '#C0C0C0',
        'sink': '#87CEEB',
        'sink_bowl': '#4682B4',
        'dishwasher': '#708090'
    }
    
    def __init__(self, measurements, scale, svg_renderer):
        self.measurements = measurements
        self.scale = scale
        self.svg_renderer = svg_renderer
        self.placed_items = []
        
    def inches_to_pixels(self, inches):
        return inches * self.scale
    
    def can_place(self, rect):
        """Check if rectangle can be placed without overlapping"""
        return not any(rect.overlaps(existing) for existing in self.placed_items)
    
    def place_item(self, rect):
        """Mark rectangle as placed"""
        self.placed_items.append(rect)
    
    def render_all(self, dwg, group, north_width, west_height):
        """Render all cabinets and appliances"""
        appliances = self.measurements.get("appliances", {})
        base_cabinets = self.measurements.get("base_cabinets", {})
        
        # Render appliances first (highest priority)
        self._render_appliances(dwg, group, north_width, west_height)
        
        # Render base cabinets
        self._render_base_cabinets(dwg, group, base_cabinets, north_width, west_height)
    
    def _render_appliance(self, dwg, group, appliance, appliance_type, north_width, west_height):
        """Generic appliance renderer"""
        location = appliance.get("location")
        
        # Calculate W3 start position
        w1_h = self.measurements["wall_measurements"]["W1"]["measurement_inches"]
        w2_h = self.measurements["wall_measurements"]["W2"]["measurement_inches"]
        w3_start = w1_h + w2_h
        
        # Calculate position based on location
        if location == "E3":
            x = north_width - appliance["depth_inches"]
            y = appliance["position_from_start_inches"]
            w = appliance["depth_inches"]
            h = appliance["width_inches"]
        elif location == "N1":
            x = appliance["position_from_start_inches"]
            y = 0
            w = appliance["width_inches"]
            h = appliance.get("depth_inches", 24)
        elif location == "S1":
            x = appliance["position_from_start_inches"]
            y = west_height - appliance["depth_inches"]
            w = appliance["width_inches"]
            h = appliance["depth_inches"]
        elif location == "W3":
            x = 0
            y = w3_start + appliance["position_from_start_inches"]
            w = appliance["depth_inches"]
            h = appliance["width_inches"]
        else:
            return
        
        rect = Rectangle(x, y, w, h, appliance_type)
        self.place_item(rect)
        
        px, py = self.inches_to_pixels(x), self.inches_to_pixels(y)
        pw, ph = self.inches_to_pixels(w), self.inches_to_pixels(h)
        
        # Render based on type
        if appliance_type == "FRIDGE":
            group.add(dwg.rect(insert=(px, py), size=(pw, ph),
                              fill=self.CABINET_COLORS['fridge'], stroke='#000', stroke_width=1))
            group.add(dwg.text('FRIDGE', insert=(px + pw/2, py + ph/2),
                              text_anchor='middle', font_size='10px', fill='#000'))
        
        elif appliance_type == "SINK":
            group.add(dwg.rect(insert=(px, py), size=(pw, ph),
                              fill=self.CABINET_COLORS['sink'], stroke='#000', stroke_width=1))
            group.add(dwg.ellipse(center=(px + pw/2, ph/2), r=(pw*0.4, ph*0.3),
                                 fill=self.CABINET_COLORS['sink_bowl'], stroke='#000', stroke_width=1))
        
        elif appliance_type == "DISHWASHER":
            group.add(dwg.rect(insert=(px, py), size=(pw, ph),
                              fill=self.CABINET_COLORS['dishwasher'], stroke='#000', stroke_width=1))
            group.add(dwg.text('DW', insert=(px + pw/2, py + ph/2),
                              text_anchor='middle', font_size='10px', fill='#FFF'))
        
        elif appliance_type in ["STOVE_MICRO", "FRIDGE_CAB_N", "FRIDGE_CAB_S"]:
            group.add(dwg.rect(insert=(px, py), size=(pw, ph),
                              fill=self.CABINET_COLORS['tall'], stroke='#000', stroke_width=2))
            if appliance_type == "STOVE_MICRO":
                group.add(dwg.text('STOVE/', insert=(px + pw/2, py + ph/2 - 5),
                                  text_anchor='middle', font_size='9px', font_weight='bold', fill='#FFF'))
                group.add(dwg.text('MICRO', insert=(px + pw/2, py + ph/2 + 5),
                                  text_anchor='middle', font_size='9px', font_weight='bold', fill='#FFF'))
            else:
                group.add(dwg.text('CAB', insert=(px + pw/2, py + ph/2 - 5),
                                  text_anchor='middle', font_size='8px', font_weight='bold', fill='#FFF'))
            group.add(dwg.text('84"H', insert=(px + pw/2, py + ph/2 + 12),
                              text_anchor='middle', font_size='8px', fill='#FFF'))
    
    def _render_appliances(self, dwg, group, north_width, west_height):
        """Render all appliances"""
        appliances = self.measurements.get("appliances", {})
        
        appliance_map = [
            ("fridge", "FRIDGE"),
            ("fridge_cabinet_north", "FRIDGE_CAB_N"),
            ("fridge_cabinet_south", "FRIDGE_CAB_S"),
            ("sink", "SINK"),
            ("dishwasher", "DISHWASHER"),
            ("stove_microwave_cabinet", "STOVE_MICRO")
        ]
        
        for key, app_type in appliance_map:
            if key in appliances:
                self._render_appliance(dwg, group, appliances[key], app_type, north_width, west_height)
    
    def _render_cabinet(self, dwg, group, cab, wall_name, index, x, y, w, h, is_lazy_susan=False):
        """Generic cabinet renderer"""
        rect = Rectangle(x, y, w, h, f"{wall_name}-{index+1}")
        if not self.can_place(rect):
            return
        
        self.place_item(rect)
        px, py = self.inches_to_pixels(x), self.inches_to_pixels(y)
        pw, ph = self.inches_to_pixels(w), self.inches_to_pixels(h)
        
        if is_lazy_susan:
            color = self.CABINET_COLORS['lazy_susan']
            group.add(dwg.rect(insert=(px, py), size=(pw, ph),
                              fill=color, stroke='#000', stroke_width=1, opacity=0.7))
            group.add(dwg.text('LS', insert=(px + pw/2, py + ph/2),
                              text_anchor='middle', font_size='10px', font_weight='bold', fill='#FFF'))
        else:
            color = self.CABINET_COLORS['base']
            group.add(dwg.rect(insert=(px, py), size=(pw, ph),
                              fill=color, stroke='#000', stroke_width=1, opacity=0.7))
            group.add(dwg.text(f'{wall_name}-{index+1}', insert=(px + pw/2, py + ph/2 - 5),
                              text_anchor='middle', font_size='9px', font_weight='bold', fill='#000'))
            group.add(dwg.text(f'{cab["width_inches"]}"W', insert=(px + pw/2, py + ph/2 + 5),
                              text_anchor='middle', font_size='8px', fill='#000'))
    
    def _render_base_cabinets(self, dwg, group, base_cabinets, north_width, west_height):
        """Render all base cabinets"""
        wall_configs = {
            "N1": {"x_calc": lambda c: c["position_from_start"], "y_calc": lambda c: 0, 
                   "w_calc": lambda c: c["width_inches"], "h_calc": lambda c: self.CABINET_DEPTH},
            "E3": {"x_calc": lambda c: north_width - self.CABINET_DEPTH, 
                   "y_calc": lambda c: c["position_from_start"],
                   "w_calc": lambda c: self.CABINET_DEPTH, "h_calc": lambda c: c["width_inches"]},
            "S1": {"x_calc": lambda c: c["position_from_start"], 
                   "y_calc": lambda c: west_height - c.get("depth_inches", self.CABINET_DEPTH),
                   "w_calc": lambda c: c["width_inches"], 
                   "h_calc": lambda c: c.get("depth_inches", self.CABINET_DEPTH)},
            "W3": {"x_calc": lambda c: 0,
                   "y_calc": lambda c: (self.measurements["wall_measurements"]["W1"]["measurement_inches"] + 
                                       self.measurements["wall_measurements"]["W2"]["measurement_inches"] + 
                                       c["position_from_start"]),
                   "w_calc": lambda c: c.get("depth_inches", self.CABINET_DEPTH),
                   "h_calc": lambda c: c["width_inches"]}
        }
        
        skip_types = ["sink_base", "dishwasher_space", "fridge_space"]
        
        for wall_name, config in wall_configs.items():
            if wall_name not in base_cabinets:
                continue
            
            for i, cab in enumerate(base_cabinets[wall_name]):
                if cab.get("type") in skip_types:
                    continue
                
                x = config["x_calc"](cab) if callable(config["x_calc"]) else config["x_calc"]()
                y = config["y_calc"](cab) if callable(config["y_calc"]) else config["y_calc"]()
                w = config["w_calc"](cab) if callable(config["w_calc"]) else config["w_calc"]()
                h = config["h_calc"](cab) if callable(config["h_calc"]) else config["h_calc"]()
                
                is_lazy_susan = cab.get("type") == "lazy_susan"
                self._render_cabinet(dwg, group, cab, wall_name, i, x, y, w, h, is_lazy_susan)
    
    def render_wall_cabinets(self, dwg, group, north_width, west_height):
        """Render all wall cabinets"""
        wall_cabinets = self.measurements.get("wall_cabinets", {})
        
        wall_configs = {
            "N1": {"x_calc": lambda c: c["position_from_start"], "y_calc": lambda c: 0,
                   "w_calc": lambda c: c["width_inches"], "h_calc": lambda c: self.CABINET_DEPTH},
            "E3": {"x_calc": lambda c: north_width - self.CABINET_DEPTH,
                   "y_calc": lambda c: c["position_from_start"],
                   "w_calc": lambda c: self.CABINET_DEPTH, "h_calc": lambda c: c["width_inches"]},
            "S1": {"x_calc": lambda c: c["position_from_start"],
                   "y_calc": lambda c: west_height - self.CABINET_DEPTH,
                   "w_calc": lambda c: c["width_inches"], "h_calc": lambda c: self.CABINET_DEPTH},
            "W3": {"x_calc": lambda c: 0,
                   "y_calc": lambda c: (self.measurements["wall_measurements"]["W1"]["measurement_inches"] +
                                       self.measurements["wall_measurements"]["W2"]["measurement_inches"] +
                                       c["position_from_start"]),
                   "w_calc": lambda c: c.get("depth_inches", self.CABINET_DEPTH),
                   "h_calc": lambda c: c["width_inches"]}
        }
        
        for wall_name, config in wall_configs.items():
            if wall_name not in wall_cabinets:
                continue
            
            for i, cab in enumerate(wall_cabinets[wall_name]):
                x = config["x_calc"](cab) if callable(config["x_calc"]) else config["x_calc"]()
                y = config["y_calc"](cab) if callable(config["y_calc"]) else config["y_calc"]()
                w = config["w_calc"](cab) if callable(config["w_calc"]) else config["w_calc"]()
                h = config["h_calc"](cab) if callable(config["h_calc"]) else config["h_calc"]()
                
                px, py = self.inches_to_pixels(x), self.inches_to_pixels(y)
                pw, ph = self.inches_to_pixels(w), self.inches_to_pixels(h)
                
                is_lazy_susan = cab.get("type") == "lazy_susan"
                
                if is_lazy_susan:
                    color = self.CABINET_COLORS['lazy_susan']
                    group.add(dwg.rect(insert=(px, py), size=(pw, ph),
                                      fill=color, stroke='#000', stroke_width=1, opacity=0.8))
                    group.add(dwg.text('LS', insert=(px + pw/2, py + ph/2),
                                      text_anchor='middle', font_size='10px', font_weight='bold', fill='#FFF'))
                else:
                    color = self.CABINET_COLORS['wall']
                    group.add(dwg.rect(insert=(px, py), size=(pw, ph),
                                      fill=color, stroke='#000', stroke_width=1, opacity=0.8))
                    label = f'{wall_name}-{i+1}'
                    if wall_name == "S1" or wall_name == "N1":
                        label += f': {cab["width_inches"]}"W'
                    else:
                        label = f'{wall_name}-{i+1}'
                    
                    group.add(dwg.text(label, insert=(px + pw/2, py + ph/2 - 3),
                                      text_anchor='middle', font_size='8px', font_weight='bold', fill='#000'))
                    group.add(dwg.text(f'{cab["height_inches"]}"H', insert=(px + pw/2, py + ph/2 + 6),
                                      text_anchor='middle', font_size='8px', fill='#000'))
