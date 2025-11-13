"""
py3dbc - 3D Bin Packing for Containers
Maritime container ship load optimization with stability physics
"""

__version__ = "1.0.0"
__author__ = "Sarth Satpute"
__license__ = "MIT"

# Import main classes for easy access
from py3dbc.maritime.container import MaritimeContainer
from py3dbc.maritime.ship import ContainerShip, Slot
from py3dbc.maritime.packer import MaritimePacker
from py3dbc.maritime.constraints import MaritimeConstraintChecker
from py3dbc.physics.stability import StabilityCalculator

__all__ = [
    "MaritimeContainer",
    "ContainerShip",
    "Slot",
    "MaritimePacker",
    "MaritimeConstraintChecker",
    "StabilityCalculator",
]