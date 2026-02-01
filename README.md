# get-in-the

Kitchen layout and design project with ASCII visualization and measurement tracking.

## Kitchen Layout

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

## Wall Measurements

- **#N1** = 87" (wall)
- **=N2** = 86" (window)
- **#W1** = 28" (wall)
- **|W2** = 31.5" (door)
- **#W3** = 72.75" (wall)
- **#S1** = 40.75" (wall)
- **|S2** = 32" (door)
- **#S3** = 4.5" (wall)
- **#E1** = 32.75" (wall)
- **#E2** = 46.75" (wall)
- **#E3** = 99.5" (wall)

## Legend

- **T**: Table
- **c**: Chair
- **F**: Fridge
- **s**: Stove
- **k**: Sink
- **-**: Counter
- **|**: Door
- **=**: Window
- **#**: Wall

## Project Structure

```
get-in-the/
├── .github/
│   ├── agents/
│   │   └── getinthe.json          # Agent configuration
│   └── prompts/
│       └── @getinthe.md           # Agent prompt/instructions
├── docs/
│   └── robots/                    # Documentation and memory
├── scripts/
│   ├── config/
│   │   ├── kitchen_measurements.json   # Room measurements
│   │   └── kitchen_analysis.json       # Layout analysis
│   ├── engine/
│   │   ├── layout_scaling_engine.py    # Scaling calculations
│   │   └── kitchen_scale_converter.py  # Measurement conversions
│   ├── kitchen_layout_generator.py     # Main layout generator
│   └── room_layout_generator.py        # Generic room layouts
└── README.md
```

## Usage

### Generate Kitchen Layout

```bash
python3 scripts/kitchen_layout_generator.py
```

This will display the kitchen layout with measurements and analysis.

### Test Scaling Engine

```bash
python3 scripts/engine/layout_scaling_engine.py
```

This will show scaling calculations and wall segment information.

## Features

- **Accurate Measurements**: All wall segments precisely measured in inches
- **ASCII Visualization**: Clear text-based layout representation
- **Scaling Engine**: Converts real measurements to character positions
- **Furniture Placement**: Support for tables, chairs, appliances, and counters
- **Work Triangle Analysis**: Validates kitchen ergonomics
- **Clearance Calculations**: Ensures proper walking and working spaces

## Agent: @getinthe

The `@getinthe` agent is a kitchen design assistant that helps with:

1. Generating accurate scaled kitchen layouts
2. Analyzing furniture placement and work triangles
3. Calculating clearances and walking spaces
4. Validating kitchen ergonomics
5. Maintaining configuration files with room measurements

Use `@getinthe` in GitHub Copilot to get help with kitchen design tasks.

