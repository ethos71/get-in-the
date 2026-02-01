#!/usr/bin/env python3
"""
Validate that all configuration files match the kitchen layout specification
"""

import json
import sys

def validate_measurements():
    """Validate wall measurements in config file"""
    
    expected_measurements = {
        "N1": 87.0,
        "N2": 86.0,
        "W1": 28.0,
        "W2": 31.5,
        "W3": 72.75,
        "S1": 40.75,
        "S2": 32.0,
        "S3": 4.5,
        "E1": 32.75,
        "E2": 46.75,
        "E3": 99.5
    }
    
    try:
        with open("scripts/config/kitchen_measurements.json", 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ Error: kitchen_measurements.json not found")
        return False
    
    wall_measurements = config.get("wall_measurements", {})
    
    print("Validating Wall Measurements:")
    print("-" * 50)
    
    all_valid = True
    
    for segment_id, expected_inches in expected_measurements.items():
        if segment_id not in wall_measurements:
            print(f"❌ {segment_id}: MISSING")
            all_valid = False
            continue
        
        actual_inches = wall_measurements[segment_id]["measurement_inches"]
        
        if actual_inches == expected_inches:
            print(f"✅ {segment_id}: {actual_inches}\" (correct)")
        else:
            print(f"❌ {segment_id}: {actual_inches}\" (expected {expected_inches}\")")
            all_valid = False
    
    # Calculate totals
    print("\nPerimeter Totals:")
    print("-" * 50)
    
    north_total = sum(wall_measurements[s]["measurement_inches"] for s in ["N1", "N2"] if s in wall_measurements)
    west_total = sum(wall_measurements[s]["measurement_inches"] for s in ["W1", "W2", "W3"] if s in wall_measurements)
    south_total = sum(wall_measurements[s]["measurement_inches"] for s in ["S1", "S2", "S3"] if s in wall_measurements)
    east_total = sum(wall_measurements[s]["measurement_inches"] for s in ["E1", "E2", "E3"] if s in wall_measurements)
    
    print(f"North Wall: {north_total}\" (expected 173\")")
    print(f"West Wall: {west_total}\" (expected 132.25\")")
    print(f"South Wall: {south_total}\" (expected 77.25\")")
    print(f"East Wall: {east_total}\" (expected 179\")")
    
    total_perimeter = north_total + west_total + south_total + east_total
    print(f"\nTotal Perimeter: {total_perimeter}\" ({total_perimeter/12:.2f}')")
    print(f"Expected: 561.5\" (46.79')")
    
    if abs(total_perimeter - 561.5) < 0.01:
        print("✅ Perimeter calculation correct")
    else:
        print("❌ Perimeter calculation incorrect")
        all_valid = False
    
    # Check layout ASCII
    print("\nLayout ASCII:")
    print("-" * 50)
    
    layout_ascii = config.get("layout_ascii", [])
    if len(layout_ascii) == 14:
        print(f"✅ Layout has correct number of lines (14)")
    else:
        print(f"❌ Layout has {len(layout_ascii)} lines (expected 14)")
        all_valid = False
    
    return all_valid


def main():
    print("=" * 50)
    print("Kitchen Layout Validation")
    print("=" * 50)
    print()
    
    if validate_measurements():
        print("\n" + "=" * 50)
        print("✅ All validations passed!")
        print("=" * 50)
        return 0
    else:
        print("\n" + "=" * 50)
        print("❌ Validation failed!")
        print("=" * 50)
        return 1


if __name__ == "__main__":
    sys.exit(main())
