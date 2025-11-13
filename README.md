<div align="center">

# 🚢 py3dbc

### 3D Bin Packing for Containers

*Maritime optimization library with ship stability physics*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Based on py3dbp](https://img.shields.io/badge/extends-py3dbp-orange)](https://github.com/jerry800416/3D-bin-packing)
---

</div>

## 📖 What is py3dbc?

**py3dbc** (3D Bin Packing for Containers) extends the popular [py3dbp](https://github.com/jerry800416/3D-bin-packing) library with **maritime-specific features** for container ship cargo optimization.

While py3dbp handles general 3D packing, it doesn't account for **ship stability physics** or **maritime safety regulations**. py3dbc bridges this gap.

---

## 🎯 Key Features

### ⚓ Ship Stability Validation
- Real-time **metacentric height (GM)** calculations
- Ensures ships won't capsize due to poor weight distribution
- Validates safety after every container placement

### 🛡️ Maritime Safety Constraints
- **Hazmat Separation:** Keeps dangerous goods at safe distances
- **Reefer Power:** Allocates refrigerated containers to powered slots
- **Weight Limits:** Enforces tier capacity and stacking restrictions
- **Regulatory Compliance:** Follows IMO and maritime standards

### 📦 Container Types
- General cargo (standard containers)
- Reefer containers (refrigerated, need power)
- Hazmat containers (dangerous goods, need separation)
- Automatic TEU calculation (20ft = 1 TEU, 40ft = 2 TEU)

### 🏗️ Realistic Ship Structure
- Discrete **bay/row/tier** slot grid (matches real ship geometry)
- 3D coordinates for each slot
- Stack weight tracking per position

---

## 🚀 Quick Start

### Installation

```bash
pip install py3dbc
```

### Basic Usage

```python
from py3dbc.maritime.ship import ContainerShip
from py3dbc.maritime.container import MaritimeContainer
from py3dbc.maritime.packer import MaritimePacker

# Create ship
ship = ContainerShip(
    ship_name='FEEDER_01',
    bays=7, rows=14, tiers=7,
    stability_params={'kg_lightship': 6.5, 'gm_min': 0.3, ...}
)

# Create containers
containers = [
    MaritimeContainer('GEN001', '20ft', 'general', 22.5, dimensions),
    MaritimeContainer('REF001', '20ft', 'reefer', 18.0, dimensions),
    MaritimeContainer('HAZ001', '20ft', 'hazmat', 14.5, dimensions)
]

# Optimize placement
packer = MaritimePacker(ship)
result = packer.pack(containers, strategy='heavy_first')

# Check results
print(f"Success Rate: {result['metrics']['placement_rate']}%")
print(f"Ship Stable: {result['metrics']['is_stable']}")
print(f"Final GM: {result['metrics']['gm']}m")
```

---

## 🧮 How It Works

### Stability Physics

py3dbc calculates **metacentric height (GM)** using naval architecture principles:

```
GM = KB + BM - KG

Where:
  KB = Center of buoyancy (ship constant)
  BM = Metacentric radius (ship geometry)
  KG = Center of gravity (changes as cargo loads)

If GM < minimum → Ship is unstable (placement rejected)
```

### Optimization Process

1. **Sort containers** (heavy first, by priority, or hazmat first)
2. **For each container:**
   - Find available slots
   - Check constraints (weight, power, separation, stability)
   - Score valid slots (tier preference, centerline, stability margin)
   - Place in best slot
3. **Update ship state** (weight, GM, occupancy)
4. **Repeat** until all containers placed or no valid slots remain

---

## 📊 Performance

Tested on realistic scenarios:
- **91% placement rate** (576 of 632 containers)
- **84% slot utilization** (vs 60-70% manual planning)
- **100% stability compliance** (GM always above minimum)
- **Processes 600+ containers in under 2 minutes**

---

## 🔧 Use Cases

- **Port Operations:** Automated cargo loading plans
- **Maritime Logistics:** Pre-planning container placement
- **Safety Validation:** Verify manual loading plans meet stability requirements
- **Training/Education:** Demonstrate naval architecture principles
- **Research:** Maritime optimization algorithms

---

## 📚 Documentation

### Main Classes

**MaritimeContainer**
- Extends py3dbp's `Item` class
- Adds cargo type, hazmat class, reefer flag, TEU value

**ContainerShip**
- Extends py3dbp's `Bin` class
- Adds bay/row/tier grid structure, stability parameters

**MaritimePacker**
- Optimization engine with constraint validation
- Multiple strategies: heavy_first, priority, hazmat_first

**StabilityCalculator**
- Naval architecture physics (GM/KG calculations)
- Real-time stability validation

**MaritimeConstraintChecker**
- Validates weight limits, hazmat separation, reefer power
- Ensures regulatory compliance

---

## 🎓 Academic Use

py3dbc was developed as part of a B.Tech final year project at **K.K. Wagh Institute of Engineering, Nashik**.

**Project:** CargoOptix - Automated Ship Load Balancing System  
**Objective:** Combine constraint-based optimization with naval architecture physics  
**Result:** Practical maritime optimization system with real-time safety validation

---

## 🤝 Contributing

Contributions welcome! Areas for enhancement:
- Genetic algorithm implementation
- Multi-port discharge sequencing
- Crane scheduling integration
- Real-time weight sensor integration
- Machine learning for slot prediction

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.


---


---

## 📞 Contact

**Project Repository:** [github.com/SarthSatpute/py3dbc](https://github.com/SarthSatpute/py3dbc)  
**Issues/Questions:** Open an issue on GitHub  
**Related Project:** [CargoOptix]([https://github.com/SarthSatpute/CargoOptix]) - Full web application using py3dbc

---

<div align="center">

**Built with ❤️ for safer, more efficient maritime operations**

⭐ Star this repo if you find it useful!

</div>
