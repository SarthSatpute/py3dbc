"""
ContainerShip class - extends Bin with maritime structure
"""
from py3dbp.main import Bin
import math


class Slot:
    """Represents a single container slot on the ship"""
    def __init__(self, slot_id, bay, row, tier, x_pos, y_pos, z_pos, 
                 max_stack_weight, max_tier_weight, is_reefer_slot=False):
        self.slot_id = slot_id
        self.bay = bay
        self.row = row
        self.tier = tier
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.z_pos = z_pos
        self.max_stack_weight = max_stack_weight
        self.max_tier_weight = max_tier_weight
        self.is_reefer_slot = is_reefer_slot
        self.occupied = False
        self.container = None
        self.current_stack_weight = 0
    
    def can_place(self, container):
        """Check if container can be placed in this slot"""
        if self.occupied:
            return False
        if container.total_weight > self.max_tier_weight:
            return False
        if container.is_reefer() and not self.is_reefer_slot:
            return False
        return True
    
    def place_container(self, container):
        """Place container in this slot"""
        self.occupied = True
        self.container = container
        self.current_stack_weight += container.total_weight
    
    def __repr__(self):
        return f"Slot({self.slot_id}, occupied={self.occupied})"


class ContainerShip(Bin):
    """
    Container ship with bay/row/tier structure
    Extends py3dbp Bin class
    """
    def __init__(self, ship_name, dimensions, bays, rows, tiers, 
                 stability_params, max_weight, bay_length=12.5, row_width=2.44):
        """
        Args:
            ship_name: Ship identifier
            dimensions: (length, beam, height) in meters
            bays: Number of bays (longitudinal sections)
            rows: Number of rows (transverse positions)
            tiers: Number of tiers (vertical levels)
            stability_params: Dict with kg_lightship, kb, bm, gm_min
            max_weight: Deadweight capacity in tonnes
            bay_length: Length of each bay in meters
            row_width: Width of each row (container width)
        """
        # Initialize parent Bin
        super().__init__(
            partno=ship_name,
            WHD=dimensions,
            max_weight=max_weight,
            corner=0,
            put_type=0
        )
        
        # Ship structure
        self.ship_name = ship_name
        self.bays = bays
        self.rows = rows
        self.tiers = tiers
        self.bay_length = bay_length
        self.row_width = row_width
        self.container_height = 2.59  # Standard container height
        
        # Stability parameters
        self.kg_lightship = stability_params['kg_lightship']
        self.lightship_weight = stability_params['lightship_weight']
        self.kb = stability_params['kb']
        self.bm = stability_params['bm']
        self.gm_min = stability_params['gm_min']
        
        # Generate slot grid
        self.slots = self._generate_slots()
        self.slot_dict = {slot.slot_id: slot for slot in self.slots}
        
        # Tracking
        self.placed_containers = []
        self.current_kg = self.kg_lightship
        self.current_gm = self.kb + self.bm - self.kg_lightship
    
    def _generate_slots(self):
        """Generate all container slots with coordinates"""
        slots = []
        slot_index = 0
        
        for bay in range(1, self.bays + 1):
            for row in range(1, self.rows + 1):
                for tier in range(1, self.tiers + 1):
                    # Calculate slot center coordinates
                    x_pos = (bay - 1) * self.bay_length + (self.bay_length / 2)
                    y_pos = -(self.width / 2) + (row - 1) * self.row_width + (self.row_width / 2)
                    z_pos = (tier - 1) * self.container_height + (self.container_height / 2)
                    
                    # Weight limits (heavier containers go lower)
                    max_stack_weight = 150 - (tier - 1) * 15
                    max_tier_weight = 30
                    
                    # Reefer slots (every 7th slot has power - roughly 14%)
                    is_reefer_slot = (slot_index % 7 == 0)
                    
                    slot_id = f"B{bay:02d}R{row:02d}T{tier:02d}"
                    
                    slot = Slot(
                        slot_id=slot_id,
                        bay=bay,
                        row=row,
                        tier=tier,
                        x_pos=round(x_pos, 2),
                        y_pos=round(y_pos, 2),
                        z_pos=round(z_pos, 2),
                        max_stack_weight=max_stack_weight,
                        max_tier_weight=max_tier_weight,
                        is_reefer_slot=is_reefer_slot
                    )
                    
                    slots.append(slot)
                    slot_index += 1
        
        return slots
    
    def get_available_slots(self):
        """Get all unoccupied slots"""
        return [slot for slot in self.slots if not slot.occupied]
    
    def get_slot(self, bay, row, tier):
        """Get specific slot by bay/row/tier"""
        slot_id = f"B{bay:02d}R{row:02d}T{tier:02d}"
        return self.slot_dict.get(slot_id)
    
    def calculate_current_stability(self):
        """Calculate current stability with placed containers"""
        if not self.placed_containers:
            return {
                'kg': self.kg_lightship,
                'gm': self.kb + self.bm - self.kg_lightship,
                'is_stable': True
            }
        
        total_moment = self.kg_lightship * self.lightship_weight
        total_weight = self.lightship_weight
        
        for container in self.placed_containers:
            if container.assigned_slot:
                slot = container.assigned_slot
                total_moment += container.total_weight * slot.z_pos
                total_weight += container.total_weight
        
        kg = total_moment / total_weight
        gm = self.kb + self.bm - kg
        
        self.current_kg = round(kg, 3)
        self.current_gm = round(gm, 3)
        
        return {
            'kg': self.current_kg,
            'gm': self.current_gm,
            'is_stable': gm >= self.gm_min,
            'total_weight': round(total_weight, 2)
        }
    
    def place_container_in_slot(self, container, slot):
        """Place container in specific slot and update tracking"""
        if not slot.can_place(container):
            return False
        
        slot.place_container(container)
        container.assigned_slot = slot
        container.bay = slot.bay
        container.row = slot.row
        container.tier = slot.tier
        container.position = [slot.x_pos, slot.y_pos, slot.z_pos]
        
        self.placed_containers.append(container)
        self.calculate_current_stability()
        
        return True
    
    def get_utilization(self):
        """Calculate slot utilization percentage"""
        occupied = len([s for s in self.slots if s.occupied])
        return round(occupied / len(self.slots) * 100, 2)
    
    def get_summary(self):
        """Get ship loading summary"""
        stability = self.calculate_current_stability()
        
        return {
            'ship_name': self.ship_name,
            'total_slots': len(self.slots),
            'occupied_slots': len(self.placed_containers),
            'utilization': self.get_utilization(),
            'total_weight': stability['total_weight'],
            'kg': stability['kg'],
            'gm': stability['gm'],
            'is_stable': stability['is_stable'],
            'containers_by_type': self._count_by_type()
        }
    
    def _count_by_type(self):
        """Count containers by cargo type"""
        counts = {'general': 0, 'reefer': 0, 'hazmat': 0}
        for container in self.placed_containers:
            counts[container.cargo_type] = counts.get(container.cargo_type, 0) + 1
        return counts
    
    def __repr__(self):
        return f"ContainerShip({self.ship_name}, {self.bays}x{self.rows}x{self.tiers}, {len(self.placed_containers)} loaded)"