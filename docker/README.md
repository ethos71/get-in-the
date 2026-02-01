# Docker Setup for Kitchen Layout Generator

This directory contains all Docker-related files for the kitchen layout generator application.

## Files

- `Dockerfile` - Main Docker image definition
- `docker-compose.yml` - Multi-service orchestration
- `.dockerignore` - Files to exclude from Docker builds
- `run.sh` - Helper script for common operations

## Quick Start

### 1. Build the Image
```bash
docker/run.sh build
```

### 2. Generate Kitchen Layouts
```bash
docker/run.sh kitchen      # Both SVG + ASCII (recommended)
docker/run.sh svg          # Default scale: 3.0 pixels/inch
docker/run.sh svg 5.0      # Custom scale: 5.0 pixels/inch
```

Output files:
- `output/kitchen_layout.svg` - Accurate SVG (open in browser)
- `output/kitchen_layout.txt` - ASCII fallback (for adjustments)

### 3. Generate ASCII Layout
```bash
docker/run.sh ascii
```

Output: `output/kitchen_layout.txt`

### 4. Validate Configuration
```bash
docker/run.sh validate
```

### 5. Interactive Shell
```bash
docker/run.sh shell
```

## Manual Docker Commands

### Build
```bash
docker compose -f docker/docker-compose.yml build
```

### Generate Kitchen Layouts
```bash
docker compose -f docker/docker-compose.yml run --rm kitchen-layout
# Generates both SVG and ASCII
```

### Generate Individual Formats
```bash
# SVG only
docker compose -f docker/docker-compose.yml run --rm kitchen-layout python scripts/engine/svg_renderer.py

# ASCII only
```bash
docker compose -f docker/docker-compose.yml --profile ascii run --rm ascii-layout
```

### Validate
```bash
docker compose -f docker/docker-compose.yml --profile validate run --rm validate
```

### Interactive Shell
```bash
docker compose -f docker/docker-compose.yml --profile shell run --rm shell
```

## Volume Mounts

The following directories are mounted for live development:

- `../output` → `/app/output` - Generated layouts persist here
- `../scripts` → `/app/scripts` - Script changes reflected immediately
- `../scripts/config` → `/app/scripts/config` - Config updates available instantly

## Image Details

- **Base**: Python 3.12 slim
- **Package Manager**: Poetry
- **Dependencies**: svgwrite (and any future additions)
- **Working Directory**: `/app`

## Cleanup

Remove all containers and images:
```bash
docker/run.sh clean
```

## Development Workflow

1. Make changes to scripts or config files
2. Run `docker/run.sh svg` or `docker/run.sh ascii`
3. Check `output/` directory for results
4. Changes to scripts are reflected immediately (volumes are mounted)
5. Changes to dependencies require `docker/run.sh build`
