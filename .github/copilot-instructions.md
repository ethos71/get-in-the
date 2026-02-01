# Copilot Instructions: Kitchen Layout Generator

## Build, Test, and Run

### Docker (Recommended)

```bash
# Build Docker image
docker/run.sh build

# Generate kitchen layouts (SVG + ASCII)
docker/run.sh kitchen          # Recommended - generates both

# Generate individual formats
docker/run.sh svg              # SVG only (default scale: 3.0 pixels/inch)
docker/run.sh svg 5.0          # SVG with custom scale
docker/run.sh ascii            # ASCII only

# Other commands
docker/run.sh validate         # Validate configuration
docker/run.sh shell            # Open interactive shell
```

### Local Development

```bash
# Setup
poetry install
poetry shell

# Generate both layouts (recommended)
poetry run python scripts/kitchen.py

# Generate individual formats
poetry run python scripts/engine/svg_renderer.py              # SVG only
poetry run python scripts/kitchen_layout_generator.py         # ASCII only
poetry run python scripts/kitchen_layout_generator.py --zoom 0.5   # ASCII with zoom

# Validate
poetry run python scripts/engine/validate_layout.py
```

### Output Files
- 📊 `output/kitchen_layout.svg` - Accurate SVG (open in browser)
- 📄 `output/kitchen_layout.txt` - ASCII fallback (for quick adjustments)

## Architecture

### Data Flow
1. **Single Source of Truth**: `scripts/config/kitchen_measurements.json` stores all room measurements
2. **Scaling Engine**: `layout_scaling_engine.py` converts real-world inches to ASCII character positions
3. **Layout Generator**: `kitchen_layout_generator.py` reads config and uses scaling engine to generate output
4. **Validation**: `validate_layout.py` verifies measurements match specification

### Key Components

**LayoutEngine** (`scripts/engine/layout_scaling_engine.py`)
- Converts inches to character positions using configurable scale factor
- Supports zoom levels (0.5x - 2.0x) while maintaining aspect ratio
- Auto-scales to fit target canvas dimensions
- Calculates wall segments maintaining L-shaped proportions

**KitchenLayoutGenerator** (`scripts/kitchen_layout_generator.py`)
- Reads from `kitchen_measurements.json` (never hardcoded values)
- Uses LayoutEngine for all position calculations
- Generates proportionally accurate ASCII visualization
- Outputs to stdout (redirect to `output/kitchen_layout.txt`)

## Key Conventions

### Measurement System
- All real-world measurements in **inches** (stored in JSON)
- Base scale: 1 character = 1 inch (before zoom)
- Zoom levels multiply the base scale (e.g., 2.0x zoom = 2 chars per inch)

### L-Shaped Room Geometry
- **North wall**: 173" (N1 + N2)
- **West wall**: 132.25" (W1 + W2 + W3) - must be continuous, no gaps
- **South wall**: 77.25" (S1 + S2 + S3) - shorter than north creates the L-shape
- **East wall**: 179" (E1 + E2 + E3) - alcove formed by E1/E2/E3 segments
- **Critical**: S1 = 90.75" in current config (note: docs show 40.75" but config is authoritative)

### Configuration-Driven Design
- Scripts **always** read from `scripts/config/kitchen_measurements.json`
- Never hardcode measurements in Python files
- Validation script checks config against specification
- Update config file, not scripts, when measurements change

### Output Conventions
- Always save generated layouts to `output/kitchen_layout.txt` for review
- Scripts output to stdout (use `>` to redirect)
- Single output file prevents multiple versions

### Symbol Legend
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

### Aspect Ratio Requirements
- North/West aspect ratio: ~1.31 (173" / 132.25")
- Must verify proportions both mathematically and visually
- Scaling engine preserves aspect ratio at all zoom levels

## Agent Configuration

The `@getinthe` agent (`.github/agents/getinthe.md` and `.github/prompts/@getinthe.md`) is specialized for kitchen layout tasks. It has detailed knowledge of the room geometry and measurement specifications.

## Best Practices

1. **Use Poetry for dependency management** - Use `poetry add <package>`, never pip directly
2. **Always activate virtual environment** - Use `poetry shell` or `source .venv/bin/activate`
3. **Verify measurements mathematically** before implementing layout changes
4. **Test proportions visually** - aspect ratio must look correct, not just calculate correctly
5. **Run validation** after config changes to ensure consistency
6. **Save all output to files** - users need to review generated layouts
7. **Use config as authority** - if docs/config conflict, config is the source of truth
