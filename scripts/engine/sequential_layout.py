"""
Sequential Layout Engine for Kitchen Cabinets

This module provides automatic positioning of cabinets along walls,
eliminating manual position_from_start calculations and preventing overlaps.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class PositionedCabinet:
    """A cabinet with calculated position."""
    type: str
    width: float
    position: float  # Auto-calculated position from wall start
    original_data: Dict[str, Any]  # Original config for rendering
    
    @property
    def end_position(self) -> float:
        """End position of this cabinet."""
        return self.position + self.width


@dataclass
class Gap:
    """A gap between cabinets."""
    start: float
    end: float
    width: float
    before: Optional[str]  # Cabinet name before gap
    after: Optional[str]  # Cabinet name after gap
    
    def suggest_cabinet_widths(self) -> List[int]:
        """Suggest standard cabinet widths that could fill this gap."""
        standard_widths = [9, 12, 15, 18, 21, 24, 30, 36]
        suggestions = []
        for width in standard_widths:
            if width <= self.width:
                remaining = self.width - width
                suggestions.append((width, remaining))
        return suggestions


@dataclass
class LayoutResult:
    """Result of layout calculation."""
    positioned_cabinets: List[PositionedCabinet]
    gaps: List[Gap]
    total_width: float
    wall_length: float
    success: bool
    errors: List[str]
    warnings: List[str]
    
    def has_issues(self) -> bool:
        """Check if layout has any errors or warnings."""
        return len(self.errors) > 0 or len(self.warnings) > 0
    
    def get_report(self) -> str:
        """Generate human-readable report."""
        lines = []
        
        if self.success:
            lines.append(f"✓ Layout successful: {self.total_width:.2f}\" used of {self.wall_length:.2f}\"")
        else:
            lines.append(f"✗ Layout failed")
        
        if self.errors:
            lines.append("\nErrors:")
            for error in self.errors:
                lines.append(f"  - {error}")
        
        if self.warnings:
            lines.append("\nWarnings:")
            for warning in self.warnings:
                lines.append(f"  - {warning}")
        
        if self.gaps:
            lines.append(f"\nGaps found ({len(self.gaps)}):")
            for i, gap in enumerate(self.gaps, 1):
                lines.append(f"  Gap {i}: {gap.width:.2f}\" at {gap.start:.2f}\"-{gap.end:.2f}\"")
                if gap.before:
                    lines.append(f"    After: {gap.before}")
                if gap.after:
                    lines.append(f"    Before: {gap.after}")
                
                # Suggest cabinet widths
                suggestions = gap.suggest_cabinet_widths()
                if suggestions:
                    lines.append(f"    Suggestions:")
                    for width, remaining in suggestions[:3]:  # Top 3
                        lines.append(f"      - {width}\" cabinet (leaves {remaining:.2f}\" gap)")
        
        return "\n".join(lines)


class SequentialLayoutEngine:
    """
    Automatically positions cabinets sequentially along a wall.
    
    Eliminates manual position_from_start calculations and prevents overlaps.
    """
    
    # Standard cabinet dimensions from Home Depot
    STANDARD_WIDTHS = [9, 12, 15, 18, 21, 24, 27, 30, 33, 36]
    BASE_DEPTH = 24
    WALL_DEPTH = 12
    
    def __init__(self, wall_length: float, min_gap_to_report: float = 1.0):
        """
        Initialize layout engine.
        
        Args:
            wall_length: Total length of wall in inches
            min_gap_to_report: Minimum gap size to report (default 1.0")
        """
        self.wall_length = wall_length
        self.min_gap_to_report = min_gap_to_report
    
    def layout_cabinets(
        self,
        cabinets: List[Dict[str, Any]],
        start_offset: float = 0.0
    ) -> LayoutResult:
        """
        Position cabinets sequentially along wall.
        
        Args:
            cabinets: List of cabinet definitions with 'type' and 'width'
            start_offset: Starting position offset (default 0.0)
        
        Returns:
            LayoutResult with positioned cabinets, gaps, and validation
        """
        positioned = []
        gaps = []
        errors = []
        warnings = []
        current_position = start_offset
        
        for i, cabinet in enumerate(cabinets):
            # Validate required fields
            if 'width' not in cabinet:
                errors.append(f"Cabinet {i}: Missing 'width' field")
                continue
            
            width = cabinet['width']
            cabinet_type = cabinet.get('type', 'cabinet')
            
            # Check for explicit gap specification
            if cabinet_type == 'gap':
                # User explicitly specified a gap
                current_position += width
                continue
            
            # Check if cabinet fits
            if current_position + width > self.wall_length:
                overhang = (current_position + width) - self.wall_length
                errors.append(
                    f"Cabinet {i} ({cabinet_type}, {width}\"): "
                    f"Extends {overhang:.2f}\" past wall end "
                    f"(position {current_position:.2f}\" + {width}\" > {self.wall_length}\")"
                )
            
            # Create positioned cabinet
            positioned_cab = PositionedCabinet(
                type=cabinet_type,
                width=width,
                position=current_position,
                original_data=cabinet
            )
            positioned.append(positioned_cab)
            
            # Check for gap before next cabinet
            if i + 1 < len(cabinets):
                next_cabinet = cabinets[i + 1]
                if next_cabinet.get('type') != 'gap' and 'position' in next_cabinet:
                    # Next cabinet has explicit position - check for gap
                    next_pos = next_cabinet['position']
                    gap_width = next_pos - positioned_cab.end_position
                    
                    if gap_width > self.min_gap_to_report:
                        gaps.append(Gap(
                            start=positioned_cab.end_position,
                            end=next_pos,
                            width=gap_width,
                            before=f"{cabinet_type} {i}",
                            after=f"{next_cabinet.get('type', 'cabinet')} {i+1}"
                        ))
                        current_position = next_pos
                        continue
                    elif gap_width < 0:
                        warnings.append(
                            f"Overlap detected: Cabinet {i} ends at {positioned_cab.end_position:.2f}\", "
                            f"but cabinet {i+1} starts at {next_pos:.2f}\""
                        )
            
            # Move to next position
            current_position += width
        
        # Check for gap at end of wall
        if current_position < self.wall_length:
            gap_width = self.wall_length - current_position
            if gap_width > self.min_gap_to_report:
                last_cabinet = positioned[-1] if positioned else None
                gaps.append(Gap(
                    start=current_position,
                    end=self.wall_length,
                    width=gap_width,
                    before=f"{last_cabinet.type}" if last_cabinet else None,
                    after="wall end"
                ))
        
        total_width = current_position - start_offset
        success = len(errors) == 0
        
        return LayoutResult(
            positioned_cabinets=positioned,
            gaps=gaps,
            total_width=total_width,
            wall_length=self.wall_length,
            success=success,
            errors=errors,
            warnings=warnings
        )
    
    def convert_to_old_format(self, result: LayoutResult, cabinet_type: str = "base") -> List[Dict[str, Any]]:
        """
        Convert positioned cabinets back to old JSON format for rendering.
        
        Args:
            result: LayoutResult from layout_cabinets()
            cabinet_type: "base" or "wall"
        
        Returns:
            List of cabinets in old format with position_from_start
        """
        cabinets = []
        depth = self.BASE_DEPTH if cabinet_type == "base" else self.WALL_DEPTH
        
        for positioned in result.positioned_cabinets:
            cabinet = positioned.original_data.copy()
            cabinet['position_from_start'] = positioned.position
            
            # Add standard depth if not specified
            if 'depth_inches' not in cabinet:
                cabinet['depth_inches'] = depth
            
            cabinets.append(cabinet)
        
        return cabinets
