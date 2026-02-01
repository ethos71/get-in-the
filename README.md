# get-in-the

Kitchen layout designer with visual floor plans.

## Quick Start

```bash
# First time setup
docker/run.sh build

# Generate your kitchen layout
docker/run.sh kitchen

# Save a milestone
docker/run.sh milestone "Added E2 door"
```

This creates two files:
- 📊 `output/kitchen_layout.svg` - Open in your browser to see the floor plan
- 📄 `output/kitchen_layout.txt` - Quick text view for making adjustments

## Commands

All user-facing commands are in `.github/commands/`:
- `kitchen.py` - Generate both SVG and ASCII layouts
- `milestone.py` - Generate layouts and commit to git

Usage:
```bash
# Docker
docker/run.sh kitchen
docker/run.sh milestone "Added E2 door"

# Local
poetry run python .github/commands/kitchen.py
poetry run python .github/commands/milestone.py -m "Added E2 door"
```

## Using @getinthe

Ask `@getinthe` in Copilot Chat to:
- Generate updated layouts
- Adjust measurements
- Validate your kitchen design
- Make changes to the floor plan
- Create milestones

Example: "@getinthe update the north wall window to 90 inches"

After changes: `docker/run.sh milestone "Updated north window"`

## Other Commands

```bash
docker/run.sh validate  # Check if measurements are correct
docker/run.sh shell     # Open interactive mode
docker/run.sh clean     # Remove containers
```

## Documentation

For technical details and how things work, see the [docs](docs/) folder.

---

**Kitchen Layout:**
- North wall: 173" (N1: 87" wall + N2: 86" alcove)
- West wall: 132.25" (door: 31.5")  
- South wall: 127.25" (door: 32")
- East wall: 179" (E2 has door: 18.25")
- L-shaped with alcoves on north and south-east

