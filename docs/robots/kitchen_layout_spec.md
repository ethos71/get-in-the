# Kitchen Layout Specification

**Last Updated:** 2026-02-01

## Overview

This document defines the exact kitchen layout specification for the get-in-the project.

## ASCII Layout

```
             N              
  ########N1######==N2===## 
  #W1                     # 
  #                       #E3 
  |W2                     # 
  #                       # 
W #                       # E
  #                       # 
  #W3                     # 
  #                  ###E2# 
  #                  #E1    
  #                  #      
  #####S1#####|S2#S3##      
              S             
```

## Wall Segment Measurements

### North Wall
- **N1**: 87" (wall segment, symbol: #)
- **N2**: 86" (window, symbol: =)
- **Total North**: 173"

### West Wall
- **W1**: 28" (wall segment, symbol: #)
- **W2**: 31.5" (door, symbol: |)
- **W3**: 72.75" (wall segment, symbol: #)
- **Total West**: 132.25"

### South Wall
- **S1**: 40.75" (wall segment, symbol: #)
- **S2**: 32" (door, symbol: |)
- **S3**: 4.5" (wall segment, symbol: #)
- **Total South**: 77.25"

### East Wall
- **E1**: 32.75" (wall segment, symbol: #)
- **E2**: 46.75" (wall segment, symbol: #)
- **E3**: 99.5" (wall segment, symbol: #)
- **Total East**: 179"

## Room Characteristics

- **Total Perimeter**: 561.5" (46.79 feet)
- **Shape**: Irregular L-shaped kitchen
- **Doors**: 2 (W2 on west wall, S2 on south wall)
- **Windows**: 1 (N2 on north wall)

## Symbol Legend

| Symbol | Meaning |
|--------|---------|
| # | Wall |
| = | Window |
| \| | Door |
| T | Table |
| c | Chair |
| F | Fridge |
| s | Stove |
| k | Sink |
| - | Counter |

## Orientation

- **N**: North (top)
- **S**: South (bottom)
- **E**: East (right)
- **W**: West (left)

## Configuration Files

All measurements are stored in:
- `scripts/config/kitchen_measurements.json` - Primary measurements and layout
- `scripts/config/kitchen_analysis.json` - Analysis data and calculations

## Usage

Generate the layout:
```bash
python3 scripts/kitchen_layout_generator.py
```

Test scaling engine:
```bash
python3 scripts/engine/layout_scaling_engine.py
```

## Notes

- The kitchen has an irregular shape with varying wall lengths
- The east wall has a recessed area (E1/E2 segments create an alcove)
- Two entry points provide good circulation
- North-facing window provides natural light
