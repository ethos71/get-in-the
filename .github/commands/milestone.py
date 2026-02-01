#!/usr/bin/env python3
"""
Milestone Command - Generate layouts and commit to git
"""

import sys
import os
import subprocess
import json
from datetime import datetime

def run_command(cmd, description):
    """Run a shell command and return success status"""
    print(f"  {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"    ❌ Failed: {e.stderr}")
        return False

def get_kitchen_summary():
    """Get summary of kitchen configuration"""
    try:
        with open("scripts/config/kitchen_measurements.json", "r") as f:
            config = json.load(f)
        
        walls = config.get("wall_measurements", {})
        north = walls["N1"]["measurement_inches"] + walls["N2"]["measurement_inches"]
        west = walls["W1"]["measurement_inches"] + walls["W2"]["measurement_inches"] + walls["W3"]["measurement_inches"]
        south = walls["S1"]["measurement_inches"] + walls["S2"]["measurement_inches"] + walls["S3"]["measurement_inches"]
        
        return f"Kitchen: N={north}\", W={west}\", S={south}\" (L-shape)"
    except:
        return "Kitchen layout"

def create_milestone(message=None, tag=None):
    """
    Create a milestone by generating layouts and committing to git
    
    Args:
        message: Optional commit message
        tag: Optional git tag
    """
    # Get project root and change to it
    project_root = os.path.join(os.path.dirname(__file__), '..', '..')
    os.chdir(project_root)
    
    print("=" * 60)
    print("Kitchen Layout Milestone")
    print("=" * 60)
    print()
    
    # Step 1: Generate layouts
    print("📐 Step 1: Generate kitchen layouts")
    sys.path.insert(0, 'scripts')
    sys.path.insert(0, 'scripts/engine')
    from svg_renderer import SVGRenderer
    from kitchen_layout_generator import KitchenLayoutGenerator
    
    try:
        # Generate SVG
        renderer = SVGRenderer(scale=3.0)
        renderer.create_kitchen_layout("output/kitchen_layout.svg")
        
        # Generate ASCII
        generator = KitchenLayoutGenerator(zoom=1.0)
        layout = generator.generate_kitchen(max_width=80, max_height=30)
        
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
        
        print("  ✅ Layouts generated")
        print()
    except Exception as e:
        print(f"  ❌ Layout generation failed: {e}")
        sys.exit(1)
    
    # Step 2: Check git status
    print("📋 Step 2: Check git status")
    if not run_command("git status --short", "Checking git status"):
        sys.exit(1)
    print()
    
    # Step 3: Stage all changes
    print("📦 Step 3: Stage changes")
    if not run_command("git add -A", "Staging all changes"):
        sys.exit(1)
    print()
    
    # Step 4: Create commit message
    if not message:
        timestamp = datetime.now().strftime("%Y-%m-%d")
        summary = get_kitchen_summary()
        message = f"Milestone {timestamp}"
    
    # Escape special characters in commit message
    message = message.replace('"', '\\"')
    
    print(f"📝 Commit message: {message}")
    print()
    
    # Step 5: Commit
    print("💾 Step 4: Commit to git")
    commit_cmd = f'git commit -m "{message}"'
    if not run_command(commit_cmd, "Creating commit"):
        print("  ℹ️  No changes to commit")
    print()
    
    # Step 6: Optional tag
    if tag:
        print(f"🏷️  Step 5: Create tag '{tag}'")
        tag_cmd = f'git tag -a "{tag}" -m "{message}"'
        if not run_command(tag_cmd, f"Creating tag {tag}"):
            print("  ⚠️  Tag creation failed")
        print()
    
    # Step 7: Push to remote
    print("🚀 Step 6: Push to remote")
    if not run_command("git push", "Pushing commits"):
        print("  ⚠️  Push failed (check remote configuration)")
    
    if tag:
        if not run_command("git push --tags", "Pushing tags"):
            print("  ⚠️  Tag push failed")
    print()
    
    # Summary
    print("=" * 60)
    print("✅ Milestone created and pushed!")
    print("=" * 60)
    print()
    print("Files committed:")
    print("  📊 output/kitchen_layout.svg")
    print("  📄 output/kitchen_layout.txt")
    print("  📝 scripts/config/kitchen_measurements.json")
    print("  📋 All project files")
    print()
    
    if tag:
        print(f"Tag: {tag}")
        print()
    
    print("View layouts: open output/kitchen_layout.svg")
    print()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Create a milestone with layouts and git commit')
    parser.add_argument('-m', '--message', type=str, help='Commit message')
    parser.add_argument('-t', '--tag', type=str, help='Git tag (e.g., v2.1.0)')
    
    args = parser.parse_args()
    
    create_milestone(message=args.message, tag=args.tag)


if __name__ == "__main__":
    main()
