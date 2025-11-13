"""
Maritime-aware packing algorithm with constraint validation
"""
from py3dbc.maritime.constraints import MaritimeConstraintChecker


class MaritimePacker:
    """
    Optimized container placement with maritime constraints and stability validation
    """
    
    def __init__(self, ship, gm_threshold=None, hazmat_separation=3):
        """
        Args:
            ship: ContainerShip instance
            gm_threshold: Minimum GM required (uses ship's gm_min if not specified)
            hazmat_separation: Minimum distance between hazmat containers
        """
        self.ship = ship
        self.gm_threshold = gm_threshold or ship.gm_min
        self.checker = MaritimeConstraintChecker(
            hazmat_separation=hazmat_separation,
            check_reefer=True,
            check_weight=True
        )
        
        self.placement_log = []
        self.failed_placements = []
    
    def pack(self, containers, strategy='heavy_first'):
        """
        Pack containers into ship using specified strategy
        
        Args:
            containers: List of MaritimeContainer objects
            strategy: 'heavy_first', 'priority', or 'hazmat_first'
            
        Returns:
            dict: {
                'success': bool,
                'placed': list of placed containers,
                'failed': list of failed containers,
                'metrics': placement metrics
            }
        """
        # Sort containers based on strategy
        sorted_containers = self._sort_containers(containers, strategy)
        
        placed = []
        failed = []
        
        print(f"\nStarting packing with strategy: {strategy}")
        print(f"Total containers to place: {len(sorted_containers)}")
        print(f"GM threshold: {self.gm_threshold}m")
        print("-" * 60)
        
        for i, container in enumerate(sorted_containers):
            print(f"\n[{i+1}/{len(sorted_containers)}] Placing {container.container_id} ({container.cargo_type}, {container.total_weight}t)...")
            
            slot = self._find_best_slot(container)
            
            if slot:
                # Place container
                success = self.ship.place_container_in_slot(container, slot)
                if success:
                    placed.append(container)
                    stability = self.ship.calculate_current_stability()
                    print(f"  ✓ Placed in {slot.slot_id}")
                    print(f"    GM: {stability['gm']}m, Total weight: {stability['total_weight']}t")
                    
                    self.placement_log.append({
                        'container': container.container_id,
                        'slot': slot.slot_id,
                        'gm': stability['gm'],
                        'weight': stability['total_weight']
                    })
                else:
                    failed.append(container)
                    print(f"  ✗ Failed to place (unknown error)")
            else:
                failed.append(container)
                print(f"  ✗ No valid slot found")
                self.failed_placements.append({
                    'container': container.container_id,
                    'reason': 'No valid slot available'
                })
        
        print("\n" + "=" * 60)
        print(f"Packing complete: {len(placed)}/{len(sorted_containers)} placed")
        print("=" * 60)
        
        metrics = self._calculate_metrics(placed, failed)
        
        return {
            'success': len(failed) == 0,
            'placed': placed,
            'failed': failed,
            'metrics': metrics,
            'placement_log': self.placement_log
        }
    
    def _sort_containers(self, containers, strategy):
        """Sort containers based on placement strategy"""
        if strategy == 'heavy_first':
            # Heavy containers go to bottom tiers
            return sorted(containers, key=lambda c: c.total_weight, reverse=True)
        
        elif strategy == 'priority':
            # High priority (low number) containers first
            return sorted(containers, key=lambda c: (c.loading_priority, -c.total_weight))
        
        elif strategy == 'hazmat_first':
            # Place hazmat early to maximize separation options
            return sorted(containers, key=lambda c: (
                0 if c.is_hazmat() else 1,
                -c.total_weight
            ))
        
        else:
            return containers
    
    def _find_best_slot(self, container):
        """
        Find best available slot for container
        
        Selection criteria:
        1. Satisfies all constraints
        2. Maintains stability (GM >= threshold)
        3. Prefers lower tiers for heavy containers
        4. Balanced transverse position (minimize list/heel)
        """
        available_slots = self.ship.get_available_slots()
        
        valid_slots = []
        
        for slot in available_slots:
            # Check constraints
            can_place, reason = self.checker.check_all_constraints(container, slot, self.ship)
            
            if not can_place:
                continue
            
            # Check stability after placement
            is_stable, predicted_gm = self.checker.validate_stability_after_placement(
                container, slot, self.ship, self.gm_threshold
            )
            
            if not is_stable:
                continue
            
            # Calculate slot score
            score = self._calculate_slot_score(container, slot, predicted_gm)
            
            valid_slots.append((slot, score, predicted_gm))
        
        if not valid_slots:
            return None
        
        # Select slot with best score
        valid_slots.sort(key=lambda x: x[1], reverse=True)
        best_slot = valid_slots[0][0]
        
        return best_slot
    
    def _calculate_slot_score(self, container, slot, predicted_gm):
        """
        Calculate desirability score for slot
        
        Higher score = better slot
        """
        score = 0
        
        # Prefer lower tiers for heavy containers
        if container.total_weight > 20:
            score += (8 - slot.tier) * 10  # Lower tier = higher score
        
        # Stability margin bonus
        stability_margin = predicted_gm - self.gm_threshold
        score += stability_margin * 20
        
        # Prefer slots closer to centerline (minimize transverse moment)
        center_row = self.ship.rows / 2
        row_distance = abs(slot.row - center_row)
        score += (center_row - row_distance) * 5
        
        # Prefer forward bays (easier discharge)
        score += slot.bay * 2
        
        return score
    
    def _calculate_metrics(self, placed, failed):
        """Calculate packing performance metrics"""
        stability = self.ship.calculate_current_stability()
        
        total_containers = len(placed) + len(failed)
        placement_rate = (len(placed) / total_containers * 100) if total_containers > 0 else 0
        
        total_teu = sum(c.teu_value for c in placed)
        teu_utilization = (total_teu / self.ship.bays / self.ship.rows / self.ship.tiers) * 100
        
        cargo_types = {'general': 0, 'reefer': 0, 'hazmat': 0}
        for c in placed:
            cargo_types[c.cargo_type] = cargo_types.get(c.cargo_type, 0) + 1
        
        return {
            'total_containers': total_containers,
            'placed_containers': len(placed),
            'failed_containers': len(failed),
            'placement_rate': round(placement_rate, 2),
            'total_teu': total_teu,
            'teu_utilization': round(teu_utilization, 2),
            'slot_utilization': self.ship.get_utilization(),
            'total_weight': stability['total_weight'],
            'kg': stability['kg'],
            'gm': stability['gm'],
            'is_stable': stability['is_stable'],
            'stability_margin': round(stability['gm'] - self.gm_threshold, 3),
            'cargo_distribution': cargo_types
        }
    
    def get_placement_summary(self):
        """Get detailed placement summary"""
        return {
            'ship_summary': self.ship.get_summary(),
            'placement_log': self.placement_log,
            'failed_placements': self.failed_placements
        }