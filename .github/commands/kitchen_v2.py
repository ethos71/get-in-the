#!/usr/bin/env python3
"""
Kitchen Layout Generator V2 - With Versioning

Uses existing config but adds automatic versioning.
"""

import sys
import shutil
from pathlib import Path
from datetime import datetime

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def archive_old_versions(output_dir: Path, max_versions: int = 25):
    """Archive existing outputs and clean up old versions."""
    versions_dir = output_dir / 'versions'
    versions_dir.mkdir(exist_ok=True)
    
    # Archive current files if they exist
    current_files = list(output_dir.glob('kitchen_layout*.svg')) + \
                   list(output_dir.glob('kitchen_layout*.txt'))
    
    if current_files:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        archived_count = 0
        for file in current_files:
            new_name = f"{file.stem}_{timestamp}{file.suffix}"
            dest = versions_dir / new_name
            shutil.copy2(file, dest)
            archived_count += 1
        print(f"📦 Archived {archived_count} files to versions/")
    
    # Clean up old versions (keep only last max_versions SVGs)
    svg_versions = sorted(versions_dir.glob('*.svg'), key=lambda p: p.stat().st_mtime)
    if len(svg_versions) > max_versions:
        to_remove = svg_versions[:-max_versions]
        for old_file in to_remove:
            # Also remove corresponding txt file
            txt_file = old_file.with_suffix('.txt')
            old_file.unlink()
            if txt_file.exists():
                txt_file.unlink()
        print(f"🗑️  Cleaned up {len(to_remove)} old versions (keeping last {max_versions})")


def main():
    """Main entry point."""
    import subprocess
    
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)
    
    # Archive old versions first
    archive_old_versions(output_dir)
    
    # Run the original kitchen command
    print("\n" + "=" * 60)
    result = subprocess.run(
        ['poetry', 'run', 'python', '.github/commands/kitchen.py'],
        cwd=Path.cwd()
    )
    
    if result.returncode == 0:
        print("\n✅ Kitchen layout generated successfully")
        print(f"📁 Output: output/kitchen_layout.svg")
        print(f"📚 Versions: {len(list((output_dir / 'versions').glob('*.svg')))} archived")
    else:
        print("\n❌ Kitchen layout generation failed")
        return result.returncode
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
