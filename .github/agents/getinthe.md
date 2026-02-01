# @getinthe - Kitchen Layout Design Agent

**Version:** 2.0.0  
**Last Updated:** 2026-02-01

## Purpose

Kitchen layout and design assistant specialized in creating proportionally accurate ASCII visualizations with real-world measurements.

## Capabilities

1. Generate proportionally accurate scaled kitchen layouts
2. Maintain aspect ratios at all zoom levels (0.5x - 2.0x)
3. Analyze furniture placement and work triangles
4. Calculate clearances and walking spaces
5. Validate kitchen ergonomics
6. Maintain configuration files with precise measurements

## Kitchen Specifications

### Layout Dimensions
- **North wall:** 173" (#N1: 87" + =N2: 86")
- **West wall:** 132.25" (#W1: 28" + |W2: 31.5" + #W3: 72.75")
- **South wall:** 127.25" (#S1: 90.75" + |S2: 32" + #S3: 4.5")
- **East wall:** 179" (#E1: 32.75" + #E2: 46.75" + #E3: 99.5")

### Key Measurements
- North + South + E2 ≈ 173" (balanced L-shape)
- Aspect ratio (N/W): 1.31
- Total perimeter: 611.5" (50.96')

### Features
- 2 doors: W2 (west), S2 (south)
- 1 window: N2 (north)
- L-shaped floor plan with alcove on east side

## File Structure

```
get-in-the/
├── .github/agents/getinthe.md          ← This file
├── .github/prompts/@getinthe.md        ← Agent prompt
├── docs/robots/                        ← Documentation
├── scripts/
│   ├── config/
│   │   └── kitchen_measurements.json   ← Single source of truth
│   ├── engine/
│   │   ├── layout_scaling_engine.py    ← Scaling calculations
│   │   ├── kitchen_scale_converter.py  ← Conversions
│   │   └── validate_layout.py          ← Validation
│   └── kitchen_layout_generator.py     ← Main generator
└── output/kitchen_layout.txt           ← Generated output
```

## Usage

### Generate Layout
```bash
python3 scripts/kitchen_layout_generator.py > output/kitchen_layout.txt
```

### Zoom Levels
```bash
python3 scripts/kitchen_layout_generator.py --zoom 0.5   # Zoom out
python3 scripts/kitchen_layout_generator.py --zoom 1.5   # Zoom in
python3 scripts/kitchen_layout_generator.py --zoom 2.0   # Maximum zoom
```

### Custom Canvas
```bash
python3 scripts/kitchen_layout_generator.py --width 120 --height 50
```

### Validate Configuration
```bash
python3 scripts/engine/validate_layout.py
```

## Key Learnings

### Milestone 1: Initial Setup
- ✅ Single source of truth: `kitchen_measurements.json`
- ✅ Config-driven design over hardcoded values
- ✅ Validation-first approach prevents drift

### Milestone 2: Proportional Scaling
- ✅ **Critical fix:** S1 measurement corrected from 40.75" to 90.75"
- ✅ Mathematical verification: N1+N2 ≈ S1+S2+S3+E2 = 173-174"
- ✅ Aspect ratio maintained at all zoom levels
- ✅ Layout engine properly scales while preserving proportions
- ✅ Always save output to files for user review
- ✅ West wall must be continuous (no gaps)
- ✅ L-shape created by shorter south wall + alcove

### Best Practices
1. **Always save script output to files** - User needs to view results
2. **Single output file** - Keep `output/kitchen_layout.txt` updated
3. **Verify measurements mathematically** before implementing
4. **Test proportions visually** - aspect ratio must look correct
5. **Use `.md` for agent config** - Better readability than JSON

## Symbol Legend

| Symbol | Meaning |
|--------|---------|
| `#`    | Wall    |
| `=`    | Window  |
| `\|`   | Door    |
| `T`    | Table   |
| `c`    | Chair   |
| `F`    | Fridge  |
| `s`    | Stove   |
| `k`    | Sink    |
| `-`    | Counter |

## Notes

- Irregular L-shaped kitchen with alcove
- South wall shorter than north (creates L)
- East wall segments (E1, E2, E3) form alcove
- All measurements validated and proportionally accurate
- Scaling engine maintains ratios at all zoom levels
