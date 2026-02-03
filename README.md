# py3dbc

**3D Bin Packing for Container Ships**

Maritime cargo optimization library with physics-based stability validation.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/py3dbc.svg)](https://pypi.org/project/py3dbc/)
[![Downloads](https://static.pepy.tech/badge/py3dbc)](https://pepy.tech/project/py3dbc)

---

## Overview

**py3dbc** (3D Bin Packing for Containers) extends the [py3dbp](https://github.com/jerry800416/3D-bin-packing) library with maritime-specific constraints and naval architecture physics for container ship cargo optimization.

While py3dbp handles general 3D bin packing, it doesn't account for ship stability physics or maritime safety regulations. py3dbc addresses this gap by integrating metacentric height (GM) calculations, hazmat separation rules, and regulatory compliance checks.

---

## Key Features

### Ship Stability Validation
- Real-time metacentric height (GM) calculation using naval architecture principles
- Dynamic center of gravity (KG) tracking during container placement
- Automatic rejection of placements that would compromise ship stability
- Compliance with IMO stability standards (GM ≥ 0.3m)

### Maritime Safety Constraints
- **Hazmat Separation:** Enforces minimum Manhattan distance between dangerous goods
- **Reefer Power Allocation:** Assigns refrigerated containers only to powered slots
- **Weight Distribution:** Validates tier capacity and stack limits
- **Regulatory Compliance:** Ensures adherence to maritime safety standards

### Container Classification
- General cargo (standard dry containers)
- Reefer containers (temperature-controlled, require power)
- Hazmat containers (dangerous goods with separation requirements)
- Automatic TEU calculation (20ft = 1 TEU, 40ft = 2 TEU)

### Realistic Ship Modeling
- Discrete bay-row-tier slot grid matching actual ship geometry
- 3D spatial coordinates for visualization
- Stack weight tracking per position
- Support for variable ship configurations

---

## Installation

```bash
pip install py3dbc
```

**Requirements:** Python 3.8+

---

## Quick Start

```python
from py3dbc.maritime.ship import ContainerShip
from py3dbc.maritime.container import MaritimeContainer
from py3dbc.maritime.packer import MaritimePacker

# Initialize ship with stability parameters
ship = ContainerShip(
    ship_name='FEEDER_01',
    dimensions=(100, 20, 15),
    bays=7,
    rows=14,
    tiers=7,
    stability_params={
        'kg_lightship': 6.5,
        'lightship_weight': 3500,
        'kb': 4.2,
        'bm': 4.5,
        'gm_min': 0.3
    },
    max_weight=8000
)

# Define containers
containers = [
    MaritimeContainer(
        container_id='GEN001',
        teu_size='20ft',
        cargo_type='general',
        total_weight=22.5,
        dimensions=(6.1, 2.4, 2.6)
    ),
    MaritimeContainer(
        container_id='REF001',
        teu_size='20ft',
        cargo_type='reefer',
        total_weight=18.0,
        dimensions=(6.1, 2.4, 2.6)
    ),
    MaritimeContainer(
        container_id='HAZ001',
        teu_size='20ft',
        cargo_type='hazmat',
        total_weight=14.5,
        dimensions=(6.1, 2.4, 2.6),
        hazmat_class='Class_3'
    )
]

# Run optimization
packer = MaritimePacker(ship, gm_threshold=0.3, hazmat_separation=3)
result = packer.pack(containers, strategy='heavy_first')

# Analyze results
print(f"Placement Success Rate: {result['metrics']['placement_rate']:.1f}%")
print(f"Ship Stability: {'STABLE' if result['metrics']['is_stable'] else 'UNSTABLE'}")
print(f"Final GM: {result['metrics']['gm']:.2f}m")
print(f"Slot Utilization: {result['metrics']['slot_utilization']:.1f}%")
```

---

## How It Works

### Stability Physics

py3dbc calculates metacentric height using fundamental naval architecture equations:

```
GM = KB + BM - KG

Where:
  KB = Vertical center of buoyancy (ship constant)
  BM = Metacentric radius (function of ship geometry)
  KG = Vertical center of gravity (updated per placement)

Stability Criterion: GM ≥ GM_min (typically 0.3m for container ships)
```

The center of gravity is recalculated after each container placement using the moment-summation method, ensuring real-time stability validation throughout the packing process.

### Optimization Algorithm

The packing algorithm follows a greedy heuristic approach with constraint validation:

1. **Sort containers** by selected strategy (heavy_first, priority, or hazmat_first)
2. **For each container:**
   - Identify all available slots matching size requirements
   - Filter slots by hard constraints (weight limits, power availability, hazmat separation)
   - Validate stability impact of each candidate placement
   - Score remaining slots using weighted heuristics (tier preference, centerline proximity, stability margin)
   - Place container in highest-scoring valid slot
3. **Update ship state** (weight distribution, GM, slot occupancy)
4. **Continue** until all containers placed or no valid slots remain

### Constraint Validation

**Weight Constraints:**
```python
Container weight ≤ Tier capacity
Stack weight ≤ Maximum stack limit (decreases with height)
```

**Hazmat Separation:**
```python
Manhattan distance = |bay₁ - bay₂| + |row₁ - row₂| + |tier₁ - tier₂|
Distance ≥ Minimum separation (default: 3 slots)
```

**Reefer Power:**
```python
Reefer containers → Only slots with power_available = True
General/Hazmat → Any available slot
```

---

## Performance

Validated on synthetic maritime scenarios:

| Metric | Result |
|--------|--------|
| Placement Success Rate | 91.1% |
| Slot Utilization | 83.9% |
| Stability Compliance | 100% |
| Processing Speed | <2s for 600+ containers |

Comparison with manual planning: 20-30% improvement in utilization while maintaining 100% stability compliance.

---

## Use Cases

- **Port Terminal Operations:** Automated generation of container loading plans
- **Maritime Logistics:** Pre-voyage cargo optimization and stowage planning
- **Safety Validation:** Verification of manual load plans against stability requirements
- **Training and Education:** Demonstration of naval architecture principles and constraint optimization
- **Research:** Algorithm development for maritime optimization problems

---

## API Reference

### Core Classes

#### `MaritimeContainer`

Extends py3dbp's `Item` class with maritime-specific attributes.

**Parameters:**
- `container_id` (str): Unique container identifier
- `teu_size` (str): '20ft' or '40ft'
- `cargo_type` (str): 'general', 'reefer', or 'hazmat'
- `total_weight` (float): Container weight in tonnes
- `dimensions` (tuple): (length, width, height) in meters
- `hazmat_class` (str, optional): Hazmat classification if applicable
- `loading_priority` (int, optional): Priority level for placement

#### `ContainerShip`

Extends py3dbp's `Bin` class with ship-specific structure and stability parameters.

**Parameters:**
- `ship_name` (str): Ship identifier
- `dimensions` (tuple): (length, beam, depth) in meters
- `bays` (int): Number of longitudinal sections
- `rows` (int): Number of transverse positions
- `tiers` (int): Number of vertical levels
- `stability_params` (dict): Naval architecture constants
- `max_weight` (float): Deadweight capacity in tonnes

#### `MaritimePacker`

Main optimization engine with integrated constraint validation.

**Parameters:**
- `ship` (ContainerShip): Ship instance to pack
- `gm_threshold` (float): Minimum acceptable GM in meters
- `hazmat_separation` (int): Minimum slot distance between hazmat containers

**Methods:**
- `pack(containers, strategy)`: Execute packing algorithm
  - Returns: Dictionary with placement results and metrics

**Available Strategies:**
- `'heavy_first'`: Sort by weight (descending)
- `'priority'`: Sort by loading priority
- `'hazmat_first'`: Place hazmat containers first

---

## Advanced Usage

### Custom Scoring Function

```python
# Modify slot scoring weights
packer = MaritimePacker(ship, gm_threshold=0.3)
packer.tier_weight = 0.4  # Prefer lower tiers
packer.stability_weight = 0.3  # Balance stability
packer.centerline_weight = 0.2  # Prefer centerline
packer.bay_weight = 0.1  # Forward placement preference
```

### Multi-Strategy Optimization

```python
strategies = ['heavy_first', 'priority', 'hazmat_first']
results = []

for strategy in strategies:
    result = packer.pack(containers.copy(), strategy=strategy)
    results.append(result)

# Select best result by placement rate
best_result = max(results, key=lambda r: r['metrics']['placement_rate'])
```




## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

---

## Citation

If you use py3dbc in academic research, please cite:

```bibtex
@software{py3dbc2025,
  author = {Satpute Sarth, Pardeshi Pranav},
  title = {py3dbc: 3D Bin Packing for Container Ships},
  year = {2025},
  publisher = {PyPI},
  url = {https://pypi.org/project/py3dbc/}
}
```

---

## Support

- **Documentation:** [GitHub Repository](https://github.com/SarthSatpute/py3dbc)
- **Issues:** [GitHub Issues](https://github.com/SarthSatpute/py3dbc/issues)
- **Discussions:** [GitHub Discussions](https://github.com/SarthSatpute/py3dbc/discussions)

---

## Related Projects

- **CargoOptix:** Full-stack web application using py3dbc for interactive cargo optimization
- **py3dbp:** Base library for general 3D bin packing (credit to original authors)

---

## Acknowledgments

Built upon the [py3dbp](https://github.com/jerry800416/3D-bin-packing) library by jerry800416.

---

**If you find this library useful, please consider starring the repository.**
