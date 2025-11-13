"""
Ship stability calculations - GM, KG, KB
"""


class StabilityCalculator:
    """
    Calculate ship stability metrics based on naval architecture principles
    """
    
    def __init__(self, ship_specs):
        """
        Args:
            ship_specs: Dictionary with keys:
                - kg_lightship: Vertical CG of empty ship (m)
                - lightship_weight: Empty ship weight (tonnes)
                - kb: Center of buoyancy above keel (m)
                - bm: Metacentric radius (m)
                - gm_min: Minimum required GM (m)
        """
        self.kg_lightship = ship_specs['kg_lightship']
        self.lightship_weight = ship_specs['lightship_weight']
        self.kb = ship_specs['kb']
        self.bm = ship_specs['bm']
        self.gm_min = ship_specs['gm_min']
    
    def calculate_kg(self, placed_containers):
        """
        Calculate vertical center of gravity (KG) with loaded containers
        
        Args:
            placed_containers: List of MaritimeContainer objects with z_pos set
            
        Returns:
            float: KG value in meters above keel
        """
        total_moment = self.kg_lightship * self.lightship_weight
        total_weight = self.lightship_weight
        
        for container in placed_containers:
            if hasattr(container, 'position') and container.position:
                z_pos = container.position[2]  # Vertical position
                total_moment += container.total_weight * z_pos
                total_weight += container.total_weight
        
        kg = total_moment / total_weight if total_weight > 0 else self.kg_lightship
        return round(kg, 3)
    
    def calculate_gm(self, kg):
        """
        Calculate metacentric height (GM)
        
        GM = KB + BM - KG
        
        Args:
            kg: Vertical center of gravity
            
        Returns:
            float: GM value in meters
        """
        gm = self.kb + self.bm - kg
        return round(gm, 3)
    
    def is_stable(self, gm):
        """
        Check if ship is stable based on GM threshold
        
        Args:
            gm: Metacentric height
            
        Returns:
            bool: True if stable (GM >= GM_min)
        """
        return gm >= self.gm_min
    
    def get_stability_status(self, placed_containers):
        """
        Calculate complete stability analysis
        
        Args:
            placed_containers: List of placed containers
            
        Returns:
            dict: {
                'kg': KG value,
                'gm': GM value,
                'is_stable': bool,
                'stability_margin': GM - GM_min,
                'total_weight': total weight
            }
        """
        kg = self.calculate_kg(placed_containers)
        gm = self.calculate_gm(kg)
        is_stable = self.is_stable(gm)
        
        total_weight = self.lightship_weight + sum(
            c.total_weight for c in placed_containers
        )
        
        return {
            'kg': kg,
            'gm': gm,
            'is_stable': is_stable,
            'stability_margin': round(gm - self.gm_min, 3),
            'total_weight': round(total_weight, 2),
            'gm_min_required': self.gm_min
        }