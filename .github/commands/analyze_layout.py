#!/usr/bin/env python3
"""
Kitchen Layout Tool - Sequential Layout System

Analyzes kitchen cabinet layouts using sequential positioning.
"""

import sys
import json
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.engine.sequential_layout import SequentialLayoutEngine


def analyze_layout(config_path: str, layout_name: str):
    """Analyze a kitchen layout and report gaps/issues."""
    
    with open(config_path) as f:
        data = json.load(f)
    
    if layout_name not in data['layouts']:
        print(f"Error: Layout '{layout_name}' not found")
        print(f"Available layouts: {list(data['layouts'].keys())}")
        return
    
    layout = data['layouts'][layout_name]
    walls = data['walls']
    
    print("=" * 60)
    print(f"Kitchen Layout Analysis: {layout_name}")
    print(f"Description: {layout.get('description', 'N/A')}")
    print("=" * 60)
    
    # Analyze base cabinets
    print("\n📦 BASE CABINETS")
    print("-" * 60)
    for wall_name, cabinets in layout['base_cabinets'].items():
        if not cabinets:
            continue
            
        wall_length = walls[wall_name]['length']
        print(f"\n{wall_name} Wall ({wall_length}\" total):")
        
        engine = SequentialLayoutEngine(wall_length=wall_length)
        result = engine.layout_cabinets(cabinets)
        
        # Print positioned cabinets
        for cab in result.positioned_cabinets:
            print(f"  {cab.position:6.2f}\"-{cab.end_position:6.2f}\": {cab.type:15s} ({cab.width}\")")
        
        # Print gaps and issues
        if result.gaps:
            print(f"\n  Gaps:")
            for gap in result.gaps:
                print(f"    {gap.start:6.2f}\"-{gap.end:6.2f}\": {gap.width:5.2f}\" gap")
                suggestions = gap.suggest_cabinet_widths()[:2]
                if suggestions:
                    print(f"      Suggestions: {', '.join([f'{w}\" ({r:.2f}\" remaining)' for w, r in suggestions])}")
        
        if result.errors:
            print(f"\n  ❌ Errors:")
            for error in result.errors:
                print(f"    {error}")
        
        if result.warnings:
            print(f"\n  ⚠️  Warnings:")
            for warning in result.warnings:
                print(f"    {warning}")
    
    # Analyze wall cabinets
    print("\n\n🗄️  WALL CABINETS")
    print("-" * 60)
    for wall_name, cabinets in layout['wall_cabinets'].items():
        if not cabinets:
            continue
            
        wall_length = walls[wall_name]['length']
        print(f"\n{wall_name} Wall ({wall_length}\" total):")
        
        engine = SequentialLayoutEngine(wall_length=wall_length)
        result = engine.layout_cabinets(cabinets)
        
        # Print positioned cabinets
        for cab in result.positioned_cabinets:
            print(f"  {cab.position:6.2f}\"-{cab.end_position:6.2f}\": {cab.type:15s} ({cab.width}\")")
        
        # Print gaps and issues
        if result.gaps:
            print(f"\n  Gaps:")
            for gap in result.gaps:
                print(f"    {gap.start:6.2f}\"-{gap.end:6.2f}\": {gap.width:5.2f}\" gap")
        
        if result.errors:
            print(f"\n  ❌ Errors:")
            for error in result.errors:
                print(f"    {error}")
    
    print("\n" + "=" * 60)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze kitchen layouts")
    parser.add_argument(
        '--config',
        default='scripts/config/kitchen_layout_simple.json',
        help='Path to kitchen config JSON'
    )
    parser.add_argument(
        '--layout',
        default='stove_on_S1',
        help='Layout name to analyze'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Analyze all layouts'
    )
    
    args = parser.parse_args()
    
    if args.all:
        with open(args.config) as f:
            data = json.load(f)
        for layout_name in data['layouts'].keys():
            analyze_layout(args.config, layout_name)
            print("\n\n")
    else:
        analyze_layout(args.config, args.layout)


if __name__ == '__main__':
    main()
