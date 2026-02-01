#!/usr/bin/env python3
"""
Kitchen Command - Generate both SVG and ASCII layouts
"""

import sys
import os

def generate_kitchen(svg_scale: float = 3.0, ascii_zoom: float = 1.0):
    """
    Generate both SVG and ASCII kitchen layouts
    
    Args:
        svg_scale: Scale factor for SVG (pixels per inch)
        ascii_zoom: Zoom level for ASCII (0.5-2.0)
    """
    # Add the scripts directory to the path
    project_root = os.path.join(os.path.dirname(__file__), '..', '..')
    os.chdir(project_root)
    sys.path.insert(0, 'scripts')
    sys.path.insert(0, 'scripts/engine')
    
    from svg_renderer import SVGRenderer
    from kitchen_layout_generator import KitchenLayoutGenerator
    
    print("=" * 60)
    print("Kitchen Layout Generator")
    print("=" * 60)
    print()
    
    # Generate SVG
    print("📐 Generating SVG layout...")
    try:
        renderer = SVGRenderer(scale=svg_scale)
        renderer.create_kitchen_layout("output/kitchen_layout.svg")
        print()
    except Exception as e:
        print(f"❌ SVG generation failed: {e}")
        print()
    
    # Generate ASCII
    print("📝 Generating ASCII layout...")
    try:
        generator = KitchenLayoutGenerator(zoom=ascii_zoom)
        layout = generator.generate_kitchen(max_width=80, max_height=30)
        
        # Save to file
        with open("output/kitchen_layout.txt", "w") as f:
            f.write("Kitchen Layout Generator - Proportionally Accurate\n")
            f.write("=" * 60 + "\n\n")
            f.write("Proportionally Accurate Kitchen Layout:\n")
            f.write(generator.layout_to_string(layout))
            f.write("\n\n")
            f.write("=" * 60 + "\n")
            f.write("Wall Measurements:\n")
            f.write("=" * 60 + "\n")
            
            measurements = generator.config.get("wall_measurements", {})
            walls = {
                "North": ["N1", "N2"],
                "West": ["W1", "W2", "W3"],
                "South": ["S1", "S2", "S3"],
                "East": ["E1", "E2", "E3"]
            }
            
            for wall_name, segs in walls.items():
                f.write(f"\n{wall_name}:\n")
                for seg in segs:
                    if seg in measurements:
                        d = measurements[seg]
                        f.write(f"  {d['symbol']}{seg} = {d['measurement_inches']}\" ({d['type']})\n")
        
        print("✅ ASCII layout saved to: output/kitchen_layout.txt")
        print()
        
        # Print preview
        print("ASCII Preview:")
        print(generator.layout_to_string(layout))
        print()
        
    except Exception as e:
        print(f"❌ ASCII generation failed: {e}")
        print()
    
    # Summary
    print("=" * 60)
    print("✅ Kitchen layouts generated!")
    print("=" * 60)
    print()
    print("Output files:")
    print("  📊 SVG:   output/kitchen_layout.svg  (open in browser)")
    print("  📄 ASCII: output/kitchen_layout.txt  (view in editor)")
    print()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate kitchen layouts (SVG + ASCII)')
    parser.add_argument('--svg-scale', type=float, default=3.0, 
                       help='SVG scale in pixels per inch (default: 3.0)')
    parser.add_argument('--ascii-zoom', type=float, default=1.0, 
                       help='ASCII zoom level 0.5-2.0 (default: 1.0)')
    
    args = parser.parse_args()
    
    generate_kitchen(svg_scale=args.svg_scale, ascii_zoom=args.ascii_zoom)


if __name__ == "__main__":
    main()
