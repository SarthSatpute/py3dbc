"""
Maritime constraint checking for container placement
"""
import math


class MaritimeConstraintChecker:
    """
    Validates maritime-specific constraints for container placement
    """
    
    def __init__(self, hazmat_separation=2, check_reefer=True, check_weight=True):
        """
        Args:
            hazmat_separation: Minimum positions between hazmat containers
            check_reefer: Enforce reefer power slot requirement
            check_weight: Enforce tier weight limits
        """
        self.hazmat_separation = hazmat_separation
        self.check_reefer = check_reefer
        self.check_weight = check_weight
    
    def check_all_constraints(self, container, slot, ship):
        """
        Check all constraints for placing container in slot
        
        Args:
            container: MaritimeContainer to place
            slot: Slot to place in
            ship: ContainerShip instance
            
        Returns:
            tuple: (can_place: bool, reason: str)
        """
        # Basic slot availability
        if slot.occupied:
            return False, "Slot already occupied"
        
        # Weight constraint
        if self.check_weight:
            can_place, reason = self.check_weight_limit(container, slot)
            if not can_place:
                return False, reason
        
        # Reefer constraint
        if self.check_reefer:
            can_place, reason = self.check_reefer_power(container, slot)
            if not can_place:
                return False, reason
        
        # Hazmat separation
        if container.is_hazmat():
            can_place, reason = self.check_hazmat_separation_constraint(
                container, slot, ship
            )
            if not can_place:
                return False, reason
        
        return True, "All constraints satisfied"
    
    def check_weight_limit(self, container, slot):
        """Check if container weight is within slot limits"""
        if container.total_weight > slot.max_tier_weight:
            return False, f"Container too heavy ({container.total_weight}t > {slot.max_tier_weight}t)"
        
        # Check cumulative stack weight
        if slot.current_stack_weight + container.total_weight > slot.max_stack_weight:
            return False, f"Stack weight limit exceeded"
        
        return True, "Weight OK"
    
    def check_reefer_power(self, container, slot):
        """Check if reefer container has power availability"""
        if container.is_reefer() and not slot.is_reefer_slot:
            return False, "Reefer container requires powered slot"
        
        return True, "Reefer OK"
    
    def check_hazmat_separation_constraint(self, container, slot, ship):
        """
        Check minimum separation distance from other hazmat containers
        
        Uses Manhattan distance in bay/row/tier space
        """
        for placed_container in ship.placed_containers:
            if placed_container.is_hazmat():
                placed_slot = placed_container.assigned_slot
                
                # Calculate distance in slot positions
                distance = self._calculate_slot_distance(slot, placed_slot)
                
                if distance < self.hazmat_separation:
                    return False, f"Too close to hazmat container {placed_container.container_id}"
        
        return True, "Hazmat separation OK"
    
    def _calculate_slot_distance(self, slot1, slot2):
        """
        Calculate Manhattan distance between slots in bay/row/tier space
        """
        bay_dist = abs(slot1.bay - slot2.bay)
        row_dist = abs(slot1.row - slot2.row)
        tier_dist = abs(slot1.tier - slot2.tier)
        
        return bay_dist + row_dist + tier_dist
    
    def check_stacking_order(self, container, slot, ship):
        """
        Check if heavier containers are below lighter ones
        (Optional additional constraint)
        """
        if slot.tier == 1:
            return True, "Bottom tier"
        
        # Check slot below
        slot_below = ship.get_slot(slot.bay, slot.row, slot.tier - 1)
        
        if not slot_below or not slot_below.occupied:
            return False, "No support below"
        
        container_below = slot_below.container
        if container.total_weight > container_below.total_weight:
            return False, "Heavier container on top of lighter one"
        
        return True, "Stacking order OK"
    
    def validate_stability_after_placement(self, container, slot, ship, gm_threshold):
        """
        Simulate placement and check if stability remains acceptable
        
        Args:
            container: Container to place
            slot: Slot to place in
            ship: Ship instance
            gm_threshold: Minimum GM required
            
        Returns:
            tuple: (is_stable: bool, gm_value: float)
        """
        # Simulate placement
        total_moment = ship.kg_lightship * ship.lightship_weight
        total_weight = ship.lightship_weight
        
        # Add existing containers
        for placed in ship.placed_containers:
            if placed.assigned_slot:
                total_moment += placed.total_weight * placed.assigned_slot.z_pos
                total_weight += placed.total_weight
        
        # Add new container
        total_moment += container.total_weight * slot.z_pos
        total_weight += container.total_weight
        
        # Calculate new KG and GM
        new_kg = total_moment / total_weight
        new_gm = ship.kb + ship.bm - new_kg
        
        is_stable = new_gm >= gm_threshold
        
        return is_stable, round(new_gm, 3)


class LoadingSequenceValidator:
    """
    Validates loading sequence for multi-port operations
    (Future extension - not critical for Review III)
    """
    
    def __init__(self):
        self.port_sequence = []
    
    def check_accessibility(self, container, slot, ship):
        """
        Check if container can be accessed for discharge
        without moving other containers
        """
        # Simplified: Just check if anything is on top
        if slot.tier < ship.tiers:
            slot_above = ship.get_slot(slot.bay, slot.row, slot.tier + 1)
            if slot_above and slot_above.occupied:
                return False, "Container blocked by container above"
        
        return True, "Accessible"