#!/usr/bin/env python3
"""
Kitchen Layout Generator - New Sequential Layout System

Generates kitchen layouts using simplified sequential positioning.
Automatically archives old versions.
"""

import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.engine.sequential_layout import SequentialLayoutEngine
from scripts.engine.svg_renderer import SVGRenderer


def archive_old_versions(output_dir: Path, max_versions: int = 25):
    """Archive existing outputs and clean up old versions."""
    versions_dir = output_dir / 'versions'
    versions_dir.mkdir(exist_ok=True)
    
    # Archive current files if they exist
    current_files = list(output_dir.glob('kitchen_layout*.svg')) + \
                   list(output_dir.glob('kitchen_layout*.txt'))
    
    if current_files:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        for file in current_files:
            new_name = f"{file.stem}_{timestamp}{file.suffix}"
            dest = versions_dir / new_name
            shutil.copy2(file, dest)
    
    # Clean up old versions (keep only last max_versions SVGs)
    svg_versions = sorted(versions_dir.glob('*.svg'), key=lambda p: p.stat().st_mtime)
    if len(svg_versions) > max_versions:
        to_remove = svg_versions[:-max_versions]
        for old_file in to_remove:
            # Also remove corresponding txt file
            txt_file = old_file.with_suffix('.txt')
            old_file.unlink()
            if txt_file.exists():
                txt_file.unlink()
        print(f"🗑️  Cleaned up {len(to_remove)} old versions")


def convert_to_old_format(layout_data: dict, walls_data: dict) -> dict:
    """Convert new simple format to old format for renderer."""
    
    old_format = {
        "wall_measurements": {},
        "appliances": {},
        "base_cabinets": {},
        "wall_cabinets": {}
    }
    
    # Convert walls - put in wall_measurements
    for wall_name, wall_info in walls_data.items():
        wall_entry = {
            "type": wall_info.get("type", "wall"),
            "measurement_inches": wall_info["length"],
            "symbol": "#" if wall_info.get("type") == "wall" else (" " if wall_info.get("type") == "entryway" else "|")
        }
        
        # Add simplified alcove representation for N2
        if wall_name == "N2" and wall_info.get("type") == "alcove":
            wall_entry["segments"] = [
                {"type": "wall", "measurement_inches": 4, "direction": "N", "symbol": "#"},
                {"type": "wall", "measurement_inches": 29.5, "direction": "NE", "symbol": "#"},
                {"type": "wall", "measurement_inches": 41.25, "direction": "E", "symbol": "#"},
                {"type": "wall", "measurement_inches": 31, "direction": "SE", "symbol": "#"}
            ]
        
        old_format["wall_measurements"][wall_name] = wall_entry
    
    # Convert appliances (already in correct format, just add location)
    for appliance_name, appliance_data in layout_data.get("appliances", {}).items():
        old_format["appliances"][appliance_name] = {
            "location": appliance_data["wall"],
            "position_from_start_inches": appliance_data["position"],
            "width_inches": appliance_data["width"],
            "depth_inches": appliance_data.get("depth", 24),
            "height_inches": appliance_data.get("height", 34),
            "notes": appliance_data.get("notes", "")
        }
    
    # Convert base cabinets
    for wall_name, cabinets in layout_data.get("base_cabinets", {}).items():
        if not cabinets:
            old_format["base_cabinets"][wall_name] = []
            continue
        
        wall_length = walls_data[wall_name]["length"]
        engine = SequentialLayoutEngine(wall_length=wall_length)
        result = engine.layout_cabinets(cabinets)
        
        converted = []
        for positioned in result.positioned_cabinets:
            cabinet = positioned.original_data.copy()
            cabinet["position_from_start"] = positioned.position
            
            # Ensure width_inches field
            if "width" in cabinet and "width_inches" not in cabinet:
                cabinet["width_inches"] = cabinet.pop("width")
            
            # Set depth
            if "depth_inches" not in cabinet:
                cabinet["depth_inches"] = 24  # Base cabinet default
            
            # Remove 'position' if it was used for explicit positioning
            cabinet.pop("position", None)
            cabinet.pop("wall", None)  # Remove wall if present
            
            converted.append(cabinet)
        
        old_format["base_cabinets"][wall_name] = converted
    
    # Convert wall cabinets
    for wall_name, cabinets in layout_data.get("wall_cabinets", {}).items():
        if not cabinets:
            old_format["wall_cabinets"][wall_name] = []
            continue
        
        wall_length = walls_data[wall_name]["length"]
        engine = SequentialLayoutEngine(wall_length=wall_length)
        result = engine.layout_cabinets(cabinets)
        
        converted = []
        for positioned in result.positioned_cabinets:
            cabinet = positioned.original_data.copy()
            cabinet["position_from_start"] = positioned.position
            
            # Ensure width_inches field
            if "width" in cabinet and "width_inches" not in cabinet:
                cabinet["width_inches"] = cabinet.pop("width")
            
            # Set depth for wall cabinets
            if "depth_inches" not in cabinet:
                if cabinet.get("type") != "lazy_susan":
                    cabinet["depth_inches"] = 12  # Wall cabinet default
            
            # Set default height
            if "height_inches" not in cabinet:
                cabinet["height_inches"] = 42
            
            # Remove 'position' and 'wall' if present
            cabinet.pop("position", None)
            cabinet.pop("wall", None)
            
            converted.append(cabinet)
        
        old_format["wall_cabinets"][wall_name] = converted
    
    return old_format


def generate_layout(config_path: str, layout_name: str, output_dir: Path):
    """Generate kitchen layout from new simple format."""
    
    # Load config
    with open(config_path) as f:
        data = json.load(f)
    
    if layout_name not in data['layouts']:
        print(f"❌ Error: Layout '{layout_name}' not found")
        print(f"Available layouts: {list(data['layouts'].keys())}")
        return False
    
    layout = data['layouts'][layout_name]
    walls = data['walls']
    
    print(f"📐 Converting layout: {layout_name}")
    print(f"   {layout.get('description', '')}")
    
    # Convert to old format
    old_format = convert_to_old_format(layout, walls)
    
    # Save temporary config for renderer
    temp_config = output_dir / '.temp_config.json'
    with open(temp_config, 'w') as f:
        json.dump(old_format, f, indent=2)
    
    # Generate SVG using existing renderer
    renderer = SVGRenderer(str(temp_config))
    renderer.create_kitchen_layout()  # This writes to output/kitchen_layout.svg
    
    # Read the generated SVG
    default_output = Path('output/kitchen_layout.svg')
    if not default_output.exists():
        print(f"❌ Error: SVG generation failed")
        temp_config.unlink()
        return False
    
    svg_content = default_output.read_text()
    
    # Clean up temp config
    temp_config.unlink()
    
    # Save SVG with layout-specific name
    svg_path = output_dir / f"kitchen_layout_{layout_name}.svg"
    with open(svg_path, 'w') as f:
        f.write(svg_content)
    
    print(f"✅ SVG saved: {svg_path}")
    
    # Generate text report
    txt_path = output_dir / f"kitchen_layout_{layout_name}.txt"
    with open(txt_path, 'w') as f:
        f.write(f"Kitchen Layout: {layout_name}\n")
        f.write(f"{layout.get('description', '')}\n")
        f.write("=" * 60 + "\n\n")
        
        # Add gap analysis
        f.write("BASE CABINETS:\n")
        f.write("-" * 60 + "\n")
        for wall_name, cabinets in layout.get("base_cabinets", {}).items():
            if not cabinets:
                continue
            wall_length = walls[wall_name]["length"]
            engine = SequentialLayoutEngine(wall_length=wall_length)
            result = engine.layout_cabinets(cabinets)
            
            f.write(f"\n{wall_name} ({wall_length}\"):\n")
            for cab in result.positioned_cabinets:
                f.write(f"  {cab.position:.2f}\"-{cab.end_position:.2f}\": {cab.type} ({cab.width}\")\n")
            
            if result.gaps:
                f.write("  Gaps:\n")
                for gap in result.gaps:
                    f.write(f"    {gap.start:.2f}\"-{gap.end:.2f}\": {gap.width:.2f}\" gap\n")
    
    print(f"✅ Report saved: {txt_path}")
    
    return True


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate kitchen layouts")
    parser.add_argument(
        '--config',
        default='scripts/config/kitchen_layout_simple.json',
        help='Path to kitchen config JSON'
    )
    parser.add_argument(
        '--layout',
        help='Layout name to generate (default: all)'
    )
    parser.add_argument(
        '--no-archive',
        action='store_true',
        help='Skip archiving old versions'
    )
    
    args = parser.parse_args()
    
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)
    
    # Archive old versions
    if not args.no_archive:
        archive_old_versions(output_dir)
    
    print("=" * 60)
    print("Kitchen Layout Generator - Sequential Layout System")
    print("=" * 60)
    
    # Load config to get layouts
    with open(args.config) as f:
        data = json.load(f)
    
    layouts_to_generate = [args.layout] if args.layout else list(data['layouts'].keys())
    
    success_count = 0
    for layout_name in layouts_to_generate:
        if generate_layout(args.config, layout_name, output_dir):
            success_count += 1
        print()
    
    print("=" * 60)
    print(f"✅ Generated {success_count}/{len(layouts_to_generate)} layouts")
    print("=" * 60)


if __name__ == '__main__':
    main()
