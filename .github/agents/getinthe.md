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
├── .github/
│   ├── agents/getinthe.md              ← This file
│   ├── prompts/@getinthe.md            ← Agent prompt
│   └── copilot-instructions.md         ← Copilot instructions
├── .venv/                              ← Virtual environment (gitignored)
├── docs/robots/                        ← Documentation
├── scripts/
│   ├── config/
│   │   └── kitchen_measurements.json   ← Single source of truth
│   ├── engine/
│   │   ├── layout_scaling_engine.py    ← Scaling calculations
│   │   ├── kitchen_scale_converter.py  ← Conversions
│   │   └── validate_layout.py          ← Validation
│   └── kitchen_layout_generator.py     ← Main generator
├── output/kitchen_layout.txt           ← Generated output
└── pyproject.toml                      ← Poetry configuration
```

## Setup

### Docker (Recommended)
```bash
docker/run.sh build
docker/run.sh svg
```

### Local Setup
```bash
# With Poetry
poetry install
poetry shell

# Or with venv
python3 -m venv .venv
source .venv/bin/activate
```

## Usage

### Docker Commands
```bash
docker/run.sh kitchen          # Generate both SVG + ASCII (recommended)
docker/run.sh svg              # Generate SVG only
docker/run.sh ascii            # Generate ASCII only
docker/run.sh validate         # Validate configuration
docker/run.sh shell            # Interactive shell
```

### Local Commands
```bash
# Generate both layouts (recommended)
poetry run python scripts/kitchen.py

# Individual formats
poetry run python scripts/engine/svg_renderer.py              # SVG only
poetry run python scripts/kitchen_layout_generator.py         # ASCII only
poetry run python scripts/kitchen_layout_generator.py --zoom 0.5   # ASCII with zoom

# Validate
poetry run python scripts/engine/validate_layout.py
```

### Output Files
- 📊 `output/kitchen_layout.svg` - Accurate SVG visualization (open in browser)
- 📄 `output/kitchen_layout.txt` - ASCII fallback (easy for adjustments)

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
1. **Use Docker for consistency** - `docker/run.sh` commands work everywhere
2. **Prefer SVG over ASCII** - Accurate dimensions without character aspect ratio issues
3. **Use Poetry for dependencies** - Never pip directly, use `poetry add`
4. **Always save script output to files** - User needs to view results
5. **Verify measurements mathematically** before implementing
6. **Test proportions visually** - aspect ratio must look correct
7. **Use `.md` for agent config** - Better readability than JSON

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
